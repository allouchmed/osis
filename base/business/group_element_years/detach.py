##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2019 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
import abc
from collections import Counter

from django.core.exceptions import ValidationError
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _, ngettext

from base.business.education_groups.group_element_year_tree import EducationGroupHierarchy
from base.business.group_element_years import management
from base.models import group_element_year
from base.models.education_group_year import EducationGroupYear
from base.models.enums.education_group_types import MiniTrainingType, TrainingType
from base.models.group_element_year import GroupElementYear


class DetachStrategy(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def is_valid(self):
        pass


class DetachEducationGroupYearStrategy(DetachStrategy):
    def __init__(self, link: GroupElementYear):
        self.link = link
        self.parent = self.link.parent
        self.education_group_year = self.link.child

    @cached_property
    def _parents(self):
        return group_element_year.find_learning_unit_formations(
            [self.parent],
            parents_as_instances=True
        )[self.parent.pk] + [self.parent]

    def get_parents_program_master(self):
        return filter(lambda elem: elem.education_group_type.name in [
            TrainingType.PGRM_MASTER_120.name,
            TrainingType.PGRM_MASTER_180_240.name
        ], self._parents)

    def _get_options_to_detach(self):
        options_to_detach = EducationGroupHierarchy(root=self.education_group_year).get_option_list()
        if self.education_group_year.education_group_type.name == MiniTrainingType.OPTION.name:
            options_to_detach += [self.education_group_year]
        return options_to_detach

    def is_valid(self):
        management.can_link_be_detached(self.parent, self.link)
        if self._get_options_to_detach() and self.get_parents_program_master():
            self._check_detatch_options_rules()
        return True

    def _check_detatch_options_rules(self):
        """
        In context of 2M when we detach an option [or group which contains option], we must ensure that
        these options are not present in MA/MD/MS
        """
        options_to_detach = self._get_options_to_detach()

        errors = []
        for master_2m in self.get_parents_program_master():
            master_2m_tree = EducationGroupHierarchy(root=master_2m)

            counter_options = Counter(master_2m_tree.get_option_list())
            counter_options.subtract(options_to_detach)
            options_to_check = [opt for opt, count in counter_options.items() if count == 0]
            if not options_to_check:
                continue

            finality_list = [elem.child for elem in master_2m_tree.to_list(flat=True)
                             if isinstance(elem.child, EducationGroupYear)
                             and elem.child.education_group_type.name in TrainingType.finality_types()]
            for finality in finality_list:
                mandatory_options = EducationGroupHierarchy(root=finality).get_option_list()
                missing_options = set(options_to_check) & set(mandatory_options)

                if missing_options:
                    errors.append(
                        ValidationError(
                            ngettext(
                                "Option \"%(acronym)s\" cannot be detach because it is contained in"
                                " %(finality_acronym)s program.",
                                "Options \"%(acronym)s\" cannot be detach because they are contained in"
                                " %(finality_acronym)s program.",
                                len(missing_options)
                            ) % {
                                "acronym": ', '.join(option.acronym for option in missing_options),
                                "finality_acronym": finality.acronym
                            })
                    )

        if errors:
            raise ValidationError(errors)


class DetachLearningUnitYearStrategy(DetachStrategy):
    def __init__(self, link: GroupElementYear):
        self.parent = link.parent
        self.learning_unit_year = link.child

    def is_valid(self):
        if self.learning_unit_year.has_or_is_prerequisite(self.parent):
            raise ValidationError(
                _("Cannot detach learning unit %(acronym)s as it has a prerequisite or it is a prerequisite.") % {
                    "acronym": self.learning_unit_year.acronym
                }
            )
        return True
