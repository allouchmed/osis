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
from datetime import datetime
from unittest import mock

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.test import TestCase
from django.urls import reverse
from waffle.testutils import override_flag

from base.forms.education_group.group import GroupYearModelForm
from base.forms.education_group.mini_training import MiniTrainingYearModelForm
from base.forms.education_group.training import TrainingEducationGroupYearForm
from base.models.enums import education_group_categories, organization_type
from base.models.enums.education_group_categories import TRAINING, Categories
from base.models.enums.entity_type import FACULTY
from base.models.exceptions import ValidationWarning
from base.tests.factories.academic_year import AcademicYearFactory, create_current_academic_year
from base.tests.factories.authorized_relationship import AuthorizedRelationshipFactory
from base.tests.factories.business.learning_units import GenerateAcademicYear
from base.tests.factories.education_group_type import EducationGroupTypeFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.entity import EntityFactory
from base.tests.factories.entity_version import EntityVersionFactory
from base.tests.factories.organization import OrganizationFactory
from base.tests.factories.person import PersonFactory, PersonWithPermissionsFactory
from base.tests.factories.person_entity import PersonEntityFactory
from reference.tests.factories.language import LanguageFactory


@override_flag('education_group_create', active=True)
class TestCreate(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.current_academic_year = create_current_academic_year()
        cls.generated_ac_years = GenerateAcademicYear(cls.current_academic_year.year + 1,
                                                      cls.current_academic_year.year + 10)
        cls.parent_education_group_year = EducationGroupYearFactory(academic_year=cls.current_academic_year)

        cls.test_categories = [
            education_group_categories.GROUP,
            education_group_categories.TRAINING,
            education_group_categories.MINI_TRAINING,
        ]

        cls.education_group_types = [
            EducationGroupTypeFactory(category=category)
            for category in cls.test_categories
        ]

        cls.urls_without_parent_by_category = {
            education_group_type.category:
                reverse(
                    "new_education_group",
                    kwargs={
                        "category": education_group_type.category,
                        "education_group_type_pk": education_group_type.pk,
                    }
                )
            for education_group_type in cls.education_group_types
        }
        cls.urls_with_parent_by_category = {
            education_group_type.category:
                reverse(
                    "new_education_group",
                    kwargs={
                        "category": education_group_type.category,
                        "education_group_type_pk": education_group_type.pk,
                        "root_id": cls.parent_education_group_year.id,
                        "parent_id": cls.parent_education_group_year.id,
                    }
                )
            for education_group_type in cls.education_group_types
        }

        cls.expected_templates_by_category = {
            education_group_categories.GROUP: "education_group/create_groups.html",
            education_group_categories.TRAINING: "education_group/create_trainings.html",
            education_group_categories.MINI_TRAINING: "education_group/create_mini_trainings.html",
        }
        cls.organization = OrganizationFactory(type=organization_type.MAIN)
        cls.entity = EntityFactory(organization=cls.organization)
        cls.entity_version = EntityVersionFactory(entity=cls.entity, entity_type=FACULTY, start_date=datetime.now())
        cls.language = LanguageFactory()
        cls.person = PersonFactory()
        PersonEntityFactory(person=cls.person, entity=cls.entity)

    def setUp(self):
        self.client.force_login(self.person.user)
        self.perm_patcher = mock.patch("base.business.education_groups.perms._is_eligible_to_add_education_group",
                                       return_value=True)
        self.mocked_perm = self.perm_patcher.start()

    def tearDown(self):
        self.perm_patcher.stop()

    def test_login_required(self):
        self.client.logout()
        for url in self.urls_without_parent_by_category.values():
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertRedirects(response, '/login/?next={}'.format(url))

    def test_permission_required(self):
        for category, url in self.urls_without_parent_by_category.items():
            with self.subTest(url=url):
                education_group_type = next(eg_type for eg_type in self.education_group_types
                                            if eg_type.category == category)
                self.client.get(url)
                self.mocked_perm.assert_called_with(self.person, None, Categories[category],
                                                    education_group_type=education_group_type,
                                                    raise_exception=True)

    def test_template_used(self):
        for category in self.test_categories:
            with self.subTest(category=category):
                response = self.client.get(self.urls_without_parent_by_category.get(category))
                self.assertTemplateUsed(response, self.expected_templates_by_category.get(category))

    def test_with_parent_set(self):
        for egt in self.education_group_types:
            AuthorizedRelationshipFactory(
                child_type=egt,
                parent_type=self.parent_education_group_year.education_group_type
            )

        for category in self.test_categories:
            with self.subTest(category=category):
                response = self.client.get(self.urls_with_parent_by_category.get(category))
                self.assertTemplateUsed(response, self.expected_templates_by_category.get(category))

    def test_response_context(self):
        expected_forms_by_category = {
            education_group_categories.GROUP: GroupYearModelForm,
            education_group_categories.TRAINING: TrainingEducationGroupYearForm,
            education_group_categories.MINI_TRAINING: MiniTrainingYearModelForm,
        }
        for category in self.test_categories:
            with self.subTest(category=category):
                response = self.client.get(self.urls_without_parent_by_category.get(category))
                form_education_group_year = response.context["form_education_group_year"]
                self.assertIsInstance(form_education_group_year, expected_forms_by_category.get(category))


@override_flag('education_group_create', active=True)
class TestCreateForm(TestCase):
    def setUp(self):
        self.current_academic_year = create_current_academic_year()
        self.generated_ac_years = GenerateAcademicYear(self.current_academic_year.year + 1,
                                                       self.current_academic_year.year + 10)
        self.parent_education_group_year = EducationGroupYearFactory(academic_year=self.current_academic_year)
        self.test_categories = [
            education_group_categories.GROUP,
            education_group_categories.TRAINING,
            education_group_categories.MINI_TRAINING,
        ]
        self.education_group_types = [
            EducationGroupTypeFactory(category=category)
            for category in self.test_categories
        ]

        self.organization = OrganizationFactory(type=organization_type.MAIN)
        self.entity = EntityFactory(organization=self.organization)
        self.entity_version = EntityVersionFactory(entity=self.entity, entity_type=FACULTY, start_date=datetime.now())
        self.language = LanguageFactory()
        self.person = PersonFactory()
        PersonEntityFactory(person=self.person, entity=self.entity)
        self.client.force_login(self.person.user)
        self.perm_patcher = mock.patch("base.business.education_groups.perms._is_eligible_to_add_education_group",
                                       return_value=True)
        self.mocked_perm = self.perm_patcher.start()

    def test_redirect_after_creation(self):
        url = reverse('new_education_group', args=[self.education_group_types[1].category,
                                                   self.education_group_types[1].id])
        data = {
            'acronym': 'YOLO1BA',
            'partial_acronym': 'LYOLO1B',
            'active': 'ACTIVE',
            'schedule_type': 'DAILY',
            'credits': '180',
            'title': 'Bachelier en',
            'academic_year': self.current_academic_year.id,
            'management_entity': self.entity_version.id,
            'administration_entity': self.entity_version.id,
            'internship': ['NO'],
            'primary_language': self.language.id,
            'diploma_printing_title': "title",
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, HttpResponseRedirect.status_code)


class TestValidateField(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.academic_year = AcademicYearFactory()

        cls.person = PersonWithPermissionsFactory("add_educationgroup")
        cls.url = reverse('validate_education_group_field', args=[TRAINING])

    def setUp(self):
        self.client.force_login(self.person.user)

        mock_clean_acronym = mock.patch(
            "base.models.education_group_year.EducationGroupYear.clean_acronym",
            return_value=None
        )
        self.mocked_clean_acronym = mock_clean_acronym.start()
        self.addCleanup(mock_clean_acronym.stop)

        mock_clean_partial_acronym = mock.patch(
            "base.models.education_group_year.EducationGroupYear.clean_partial_acronym",
            return_value=None
        )
        self.mocked_clean_partial_acronym = mock_clean_partial_acronym.start()
        self.addCleanup(mock_clean_partial_acronym.stop)

    def test_response_should_be_empty_when_fields_are_valid(self):
        response = self.client.get(
            self.url,
            data={"academic_year": self.academic_year.pk, "acronym": "TEST"},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {}
        )

    def test_response_should_contain_error_message_when_field_not_valid(self):
        self.mocked_clean_acronym.side_effect = ValidationError({"acronym": "error acronym"})
        self.mocked_clean_partial_acronym.side_effect = ValidationWarning({"partial_acronym": "error partial"})

        response = self.client.get(
            self.url,
            data={"academic_year": self.academic_year.pk, "acronym": "TEST"},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {"acronym": {"msg": "error acronym", "level": messages.DEFAULT_TAGS[messages.ERROR]},
             "partial_acronym": {"msg": "error partial", "level": messages.DEFAULT_TAGS[messages.WARNING]}}
        )
