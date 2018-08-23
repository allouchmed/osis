##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2017 Université catholique de Louvain (http://www.uclouvain.be)
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

from django.test import TestCase

from base.business.education_groups.postponement import _model_to_dict
from base.forms.education_group.training import TrainingForm
from base.models.education_group_year import EducationGroupYear
from base.models.enums import education_group_categories, internship_presence
from base.models.enums.active_status import ACTIVE
from base.models.enums.schedule_type import DAILY
from base.tests.factories.academic_year import create_current_academic_year, get_current_year
from base.tests.factories.business.learning_units import GenerateAcademicYear
from base.tests.factories.education_group_type import EducationGroupTypeFactory
from base.tests.factories.education_group_year import TrainingFactory, EducationGroupYearFactory
from base.tests.factories.education_group_year_domain import EducationGroupYearDomainFactory
from base.tests.factories.entity_version import MainEntityVersionFactory, EntityVersionFactory
from base.tests.factories.user import UserFactory
from reference.tests.factories.domain import DomainFactory
from reference.tests.factories.language import LanguageFactory


class TestPostponementEducationGroupYearMixin(TestCase):
    def setUp(self):

        self.education_group_year = TrainingFactory(academic_year=create_current_academic_year())
        self.education_group_type = EducationGroupTypeFactory(
            category=education_group_categories.TRAINING
        )

        EntityVersionFactory(entity=self.education_group_year.administration_entity)
        EntityVersionFactory(entity=self.education_group_year.management_entity)
        self.list_acs = GenerateAcademicYear(get_current_year(), get_current_year()+40).academic_years

        self.data = {
            'title': 'Métamorphose',
            'title_english': 'Transfiguration',
            'education_group_type': self.education_group_type.pk,
            'credits': 42,
            'acronym': 'CRSCHOIXDVLD',
            'partial_acronym': 'LDVLD101R',
            'management_entity': MainEntityVersionFactory().pk,
            'administration_entity': MainEntityVersionFactory().pk,
            'main_teaching_campus': "",
            'academic_year': create_current_academic_year().pk,
            'active': ACTIVE,
            'schedule_type': DAILY,
            "internship": internship_presence.NO,
            "primary_language": LanguageFactory().pk,
            "start_year": 2010,
        }

    def test_init(self):
        # In case of creation
        form = TrainingForm({}, user=UserFactory(), education_group_type=self.education_group_type)
        self.assertFalse(hasattr(form, "dict_initial_egy"))

        # In case of update
        form = TrainingForm(
            {},
            user=UserFactory(),
            instance=self.education_group_year
        )
        dict_initial_egy = _model_to_dict(
            self.education_group_year, exclude=form.field_to_exclude
        )

        self.assertEqual(str(form.dict_initial_egy), str(dict_initial_egy))

    def test_save_with_postponement(self):
        # Create postponed egy
        form = TrainingForm(
            self.data,
            instance=self.education_group_year,
            user=UserFactory()
        )
        self.assertTrue(form.is_valid(), form.errors)
        form.save()

        self.assertEqual(len(form.education_group_year_postponed), 6)

        self.assertEqual(
            EducationGroupYear.objects
                .filter(education_group=self.education_group_year.education_group)
                .count(), 7
        )
        self.assertEqual(len(form.warnings), 0)

        # Update egys
        self.education_group_year.refresh_from_db()

        self.data["title"] = "Defence Against the Dark Arts"
        form = TrainingForm(self.data, instance=self.education_group_year, user=UserFactory())
        self.assertTrue(form.is_valid(), form.errors)
        form.save()

        self.assertEqual(
            EducationGroupYear.objects.filter(
                education_group=self.education_group_year.education_group
            ).count(), 7
        )
        self.assertEqual(len(form.warnings), 0, form.warnings)

    def test_save_with_postponement_error(self):
        EducationGroupYearFactory(academic_year=self.list_acs[4],
                                  education_group=self.education_group_year.education_group)

        form = TrainingForm(
            self.data,
            instance=self.education_group_year,
            user=UserFactory()
        )
        self.assertTrue(form.is_valid(), form.errors)
        form.save()

        self.assertEqual(len(form.education_group_year_postponed), 5)

        self.assertEqual(
            EducationGroupYear.objects.filter(
                education_group=self.education_group_year.education_group).count(), 7
        )
        self.assertEqual(len(form.warnings), 13)

    def test_save_with_postponement_m2m(self):
        domains = [DomainFactory(name="Alchemy"), DomainFactory(name="Muggle Studies")]

        self.data["secondary_domains"] = '|'.join([str(domain.pk) for domain in domains])

        form = TrainingForm(
            self.data,
            instance=self.education_group_year,
            user=UserFactory()
        )
        self.assertTrue(form.is_valid(), form.errors)
        form.save()

        self.assertEqual(len(form.education_group_year_postponed), 6)

        self.assertEqual(
            EducationGroupYear.objects
                .filter(education_group=self.education_group_year.education_group)
                .count(), 7
        )
        last = EducationGroupYear.objects.filter(education_group=self.education_group_year.education_group
                                                 ).order_by('academic_year').last()

        self.education_group_year.refresh_from_db()
        self.assertEqual(self.education_group_year.secondary_domains.count(), 2)
        self.assertEqual(last.secondary_domains.count(), 2)
        self.assertEqual(len(form.warnings), 0)

        # update with a conflict
        dom3 = DomainFactory(name="Divination")
        EducationGroupYearDomainFactory(domain=dom3, education_group_year=last)

        domains = [DomainFactory(name="Care of Magical Creatures"), DomainFactory(name="Muggle Studies")]

        self.data["secondary_domains"] = '|'.join([str(domain.pk) for domain in domains])

        form = TrainingForm(self.data, instance=self.education_group_year, user=UserFactory())
        self.assertTrue(form.is_valid(), form.errors)
        form.save()

        self.assertEqual(len(form.education_group_year_postponed), 5)

        self.assertEqual(
            EducationGroupYear.objects
                .filter(education_group=self.education_group_year.education_group)
                .count(), 7
        )
        last.refresh_from_db()
        self.education_group_year.refresh_from_db()

        self.assertEqual(self.education_group_year.secondary_domains.count(), 2)
        self.assertEqual(last.secondary_domains.count(), 3)
        self.assertEqual(len(form.warnings), 1)
