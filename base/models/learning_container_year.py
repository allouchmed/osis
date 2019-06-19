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
from django.db import models
from django.utils.translation import ugettext_lazy as _
from reversion.admin import VersionAdmin

from base.business.learning_container_year import get_learning_container_year_warnings
from base.models import learning_unit_year
from base.models.enums import learning_unit_year_subtypes
from base.models.enums import vacant_declaration_type
from base.models.enums.learning_container_year_types import LearningContainerYearType
from osis_common.models.serializable_model import SerializableModel, SerializableModelAdmin

FIELDS_FOR_COMPARISON = ['team', 'is_vacant', 'type_declaration_vacant']


class LearningContainerYearAdmin(VersionAdmin, SerializableModelAdmin):
    list_display = ('learning_container', 'academic_year', 'container_type', 'acronym', 'common_title')
    search_fields = ['acronym']
    list_filter = ('academic_year', 'in_charge', 'is_vacant',)


class LearningContainerYear(SerializableModel):
    external_id = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    academic_year = models.ForeignKey('AcademicYear', on_delete=models.CASCADE)
    learning_container = models.ForeignKey('LearningContainer', on_delete=models.CASCADE)

    container_type = models.CharField(
        verbose_name=_('Type'),
        db_index=True,
        max_length=20,
        choices=LearningContainerYearType.choices(),
    )

    common_title = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('Common title'))
    common_title_english = models.CharField(max_length=250, blank=True, null=True,
                                            verbose_name=_('Common English title'))
    acronym = models.CharField(max_length=10)
    changed = models.DateTimeField(null=True, auto_now=True)
    team = models.BooleanField(default=False, verbose_name=_('Team management'))
    is_vacant = models.BooleanField(default=False, verbose_name=_('Vacant'))
    type_declaration_vacant = models.CharField(max_length=100, blank=True, null=True,
                                               verbose_name=_('Decision'),
                                               choices=vacant_declaration_type.DECLARATION_TYPE)
    in_charge = models.BooleanField(default=False)

    _warnings = None

    def __str__(self):
        return u"%s - %s" % (self.acronym, self.common_title)

    class Meta:
        unique_together = ("learning_container", "academic_year",)
        permissions = (
            ("can_access_learningcontaineryear", "Can access learning container year"),
        )

    @property
    def warnings(self):
        if self._warnings is None:
            self._warnings = get_learning_container_year_warnings(self)
        return self._warnings

    def get_partims_related(self):
        return learning_unit_year.search(learning_container_year_id=self,
                                         subtype=learning_unit_year_subtypes.PARTIM).order_by('acronym')

    def is_type_for_faculty(self) -> bool:
        return self.container_type in LearningContainerYearType.for_faculty()
