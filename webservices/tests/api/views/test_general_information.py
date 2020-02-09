##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2018 Université catholique de Louvain (http://www.uclouvain.be)
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
from unittest import mock

from django.conf import settings
from django.db.models import Value, CharField
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from base.business.education_groups.general_information_sections import DETAILED_PROGRAM, \
    SKILLS_AND_ACHIEVEMENTS, COMMON_DIDACTIC_PURPOSES, INTRODUCTION
from base.models.education_group_year import EducationGroupYear
from base.models.enums.education_group_types import TrainingType, GroupType
from base.tests.factories.education_group_year import EducationGroupYearFactory, EducationGroupYearCommonFactory, \
    TrainingFactory
from base.tests.factories.group_element_year import GroupElementYearFactory
from base.tests.factories.person import PersonFactory
from cms.enums.entity_name import OFFER_YEAR
from cms.tests.factories.translated_text import TranslatedTextFactory
from cms.tests.factories.translated_text_label import TranslatedTextLabelFactory
from webservices.api.serializers.general_information import GeneralInformationSerializer
from webservices.business import SKILLS_AND_ACHIEVEMENTS_INTRO, SKILLS_AND_ACHIEVEMENTS_EXTRA
from webservices.tests.api.serializers.test_general_information import _get_mocked_sections_per_offer_type
from webservices.tests.api.test_utils import get_annotated_egy_qs


class GeneralInformationTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.person = PersonFactory()
        cls.language = settings.LANGUAGE_CODE_EN
        cls.egy = EducationGroupYearFactory()
        common_egy = EducationGroupYearCommonFactory(academic_year=cls.egy.academic_year)
        cls.pertinent_sections = {
            'specific': [DETAILED_PROGRAM, SKILLS_AND_ACHIEVEMENTS],
            'common': [COMMON_DIDACTIC_PURPOSES]
        }
        cls.annotations = {}
        for section in cls.pertinent_sections['common']:
            t_label = TranslatedTextLabelFactory(language=cls.language, text_label__label=section)
            t = TranslatedTextFactory(
                reference=common_egy.id,
                entity=OFFER_YEAR,
                language=cls.language,
                text_label__label=section
            )
            cls.annotations.update({'common_' + section: (t_label.label, t.text)})
        for section in cls.pertinent_sections['specific']:
            t_label = TranslatedTextLabelFactory(language=cls.language, text_label__label=section)
            t = TranslatedTextFactory(
                reference=cls.egy.id,
                entity=OFFER_YEAR,
                language=cls.language,
                text_label__label=section
            )
            cls.annotations.update({section: (t_label.label, t.text)})
        for label in [SKILLS_AND_ACHIEVEMENTS_INTRO, SKILLS_AND_ACHIEVEMENTS_EXTRA]:
            TranslatedTextFactory(
                text_label__label=label,
                reference=cls.egy.id,
                entity=OFFER_YEAR,
                language=cls.language
            )
        cls.url = reverse('generalinformations_read', kwargs={
            'acronym': cls.egy.acronym,
            'year': cls.egy.academic_year.year,
            'language': cls.language
        })

    def setUp(self):
        sections_patcher = mock.patch(
            "base.business.education_groups.general_information_sections.SECTIONS_PER_OFFER_TYPE",
            {self.egy.education_group_type.name: self.pertinent_sections}
        )
        sections_patcher.start()
        self.addCleanup(sections_patcher.stop)
        self.client.force_authenticate(user=self.person.user)
        self.annotated_egy_qs = get_annotated_egy_qs(self.egy, self.annotations)
        self.annotated_egy = self.annotated_egy_qs.first()

    def test_get_not_authorized(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_method_not_allowed(self):
        methods_not_allowed = ['post', 'delete', 'put', 'patch']

        for method in methods_not_allowed:
            response = getattr(self.client, method)(self.url)
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_results_case_education_group_year_not_found(self):
        invalid_url = reverse('generalinformations_read', kwargs={
            'acronym': 'dummy',
            'year': 2019,
            'language': settings.LANGUAGE_CODE_EN
        })
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_results_based_on_egy_with_acronym(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        serializer = GeneralInformationSerializer(
            self.annotated_egy, context={
                'language': self.language,
                'acronym': self.egy.acronym
            }
        )
        self.assertEqual(response.data, serializer.data)

    def test_get_results_based_on_egy_with_partial_acronym(self):
        url_partial_acronym = reverse('generalinformations_read', kwargs={
            'acronym': self.egy.partial_acronym,
            'year': self.egy.academic_year.year,
            'language': self.language
        })

        response = self.client.get(url_partial_acronym)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        serializer = GeneralInformationSerializer(
            self.annotated_egy, context={
                'language': self.language,
                'acronym': self.egy.partial_acronym
            }
        )
        self.assertEqual(response.data, serializer.data)


class IntroOffersSectionTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.egy = TrainingFactory(education_group_type__name=TrainingType.PGRM_MASTER_120.name)
        EducationGroupYearCommonFactory(academic_year=cls.egy.academic_year)
        cls.language = settings.LANGUAGE_CODE_FR[:2]

    def setUp(self):
        patcher_sections = mock.patch(
            'base.business.education_groups.general_information_sections.SECTIONS_PER_OFFER_TYPE',
            _get_mocked_sections_per_offer_type(self.egy)
        )
        patcher_sections.start()
        self.addCleanup(patcher_sections.stop)
        self.client.force_authenticate(user=PersonFactory().user)
        self.url = reverse('generalinformations_read', kwargs={
            'acronym': self.egy.acronym,
            'year': self.egy.academic_year.year,
            'language': self.language
        })

    def test_get_intro_offers(self):
        gey = GroupElementYearFactory(
            parent=self.egy,
            child_branch__education_group_type__name=GroupType.COMMON_CORE.name,
            child_branch__partial_acronym="TESTTC"
        )
        intro_offer_section, expected_text = self._get_pertinent_intro_section(gey)
        response = self.client.get(self.url)
        self.assertEqual(response.data, intro_offer_section)

    def _get_pertinent_intro_section(self, gey):
        t_label = TranslatedTextLabelFactory(
            text_label__label=INTRODUCTION,
            language=self.language,
        )
        expected_text = TranslatedTextFactory(
            text_label__label=INTRODUCTION,
            language=self.language,
            entity=OFFER_YEAR,
            reference=gey.child_branch.id
        )
        annotated_egy = EducationGroupYear.objects.filter(id=self.egy.id).annotate(**{
            'intro-' + gey.child_branch.partial_acronym: Value(expected_text.text, output_field=CharField()),
            'intro': Value(t_label.label, output_field=CharField())
        })
        return GeneralInformationSerializer(
            annotated_egy.first(), context={
                'language': self.language,
                'acronym': self.egy.acronym,
                'intro_offers': [gey.child_branch.partial_acronym]
            }
        ).data, expected_text.text
