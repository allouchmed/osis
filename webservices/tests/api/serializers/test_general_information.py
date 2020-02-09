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
import collections
from unittest import mock

from django.conf import settings
from django.db.models import CharField, Value
from django.test import TestCase

from base.business.education_groups.general_information_sections import DETAILED_PROGRAM, \
    COMMON_DIDACTIC_PURPOSES, SKILLS_AND_ACHIEVEMENTS, WELCOME_INTRODUCTION, INTRODUCTION
from base.models.education_group_year import EducationGroupYear
from base.models.enums.education_group_types import GroupType, MiniTrainingType, TrainingType
from base.tests.factories.education_group_year import EducationGroupYearCommonFactory, \
    TrainingFactory
from base.tests.factories.group_element_year import GroupElementYearFactory
from cms.enums.entity_name import OFFER_YEAR
from cms.tests.factories.translated_text import TranslatedTextFactory
from cms.tests.factories.translated_text_label import TranslatedTextLabelFactory
from webservices.api.serializers.general_information import GeneralInformationSerializer
from webservices.business import EVALUATION_KEY
from webservices.tests.api.test_utils import get_annotated_egy_qs, create_cms_texts


class GeneralInformationSerializerTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.egy = TrainingFactory(education_group_type__name=TrainingType.PGRM_MASTER_120.name)
        cls.common_egy = EducationGroupYearCommonFactory(academic_year=cls.egy.academic_year)
        cls.language = settings.LANGUAGE_CODE_EN
        cls.pertinent_sections = {
            'specific': [DETAILED_PROGRAM, SKILLS_AND_ACHIEVEMENTS],
            'common': [COMMON_DIDACTIC_PURPOSES]
        }
        cls.annotations = {}
        for section in cls.pertinent_sections['common']:
            t_label = TranslatedTextLabelFactory(
                language=cls.language,
                text_label__label=section
            )
            t = TranslatedTextFactory(
                reference=cls.common_egy.id,
                entity=OFFER_YEAR,
                language=cls.language,
                text_label__label=section,
            )
            cls.annotations.update({'common_' + section: (t_label.label, t.text)})
        create_cms_texts(cls.language, cls.egy, cls.annotations, cls.pertinent_sections['specific'])

    def setUp(self):
        patcher_sections = mock.patch(
            'base.business.education_groups.general_information_sections.SECTIONS_PER_OFFER_TYPE',
            _get_mocked_sections_per_offer_type(self.egy, **self.pertinent_sections)
        )
        patcher_sections.start()
        self.addCleanup(patcher_sections.stop)
        self.annotated_egy_qs = get_annotated_egy_qs(self.egy, self.annotations)
        self.annotated_egy = self.annotated_egy_qs.first()
        self.serializer = GeneralInformationSerializer(
            self.annotated_egy, context={
                'language': self.language,
                'acronym': self.egy.acronym
            }
        )

    def test_contains_expected_fields(self):
        expected_fields = [
            'language',
            'acronym',
            'title',
            'year',
            'education_group_type',
            'education_group_type_text',
            'sections'
        ]
        self.assertListEqual(list(self.serializer.data.keys()), expected_fields)

    def test_ensure_content_field_is_list_of_dict(self):
        expected_fields = [
            'id',
            'label',
            'content',
        ]
        self.assertEqual(type(self.serializer.data['sections']), list)
        self.assertEqual(
            len(self.serializer.data['sections']),
            len(self.pertinent_sections['common'] + self.pertinent_sections['specific'])
        )
        for section in self.serializer.data['sections']:
            if section['id'] == EVALUATION_KEY:
                self.assertTrue(isinstance(section, dict))
                self.assertListEqual(list(section.keys()), expected_fields + ['free_text'])
            else:
                self.assertTrue(isinstance(section, collections.OrderedDict))
                self.assertListEqual(list(section.keys()), expected_fields)

    def test_case_text_not_existing(self):
        with mock.patch(
                'base.business.education_groups.general_information_sections.SECTIONS_PER_OFFER_TYPE',
                _get_mocked_sections_per_offer_type(self.egy, specific=[WELCOME_INTRODUCTION])
        ):
            t_label = TranslatedTextLabelFactory(
                language=self.language,
                text_label__label=WELCOME_INTRODUCTION
            )
            self.annotated_egy_qs = self.annotated_egy_qs.annotate(
                welcome_introduction_label=Value(t_label.label, output_field=CharField())
            )
            welcome_introduction_section = GeneralInformationSerializer(
                self.annotated_egy_qs.first(), context={
                    'language': self.language,
                    'acronym': self.egy.acronym
                }
            ).data['sections'][0]
            self.assertIsNone(welcome_introduction_section['content'])


def _get_mocked_sections_per_offer_type(egy, specific=None, common=None):
    return {
        egy.education_group_type.name: {
            'specific': specific or [],
            'common': common or []
        }
    }


class IntroOffersSectionTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.egy = TrainingFactory(education_group_type__name=TrainingType.PGRM_MASTER_120.name)
        EducationGroupYearCommonFactory(academic_year=cls.egy.academic_year)
        cls.language = settings.LANGUAGE_CODE_EN

    def setUp(self):
        patcher_sections = mock.patch(
            'base.business.education_groups.general_information_sections.SECTIONS_PER_OFFER_TYPE',
            _get_mocked_sections_per_offer_type(self.egy)
        )
        patcher_sections.start()
        self.addCleanup(patcher_sections.stop)

    def test_get_intro_offers(self):
        gey = GroupElementYearFactory(
            parent=self.egy,
            child_branch__education_group_type__name=GroupType.COMMON_CORE.name,
            child_branch__partial_acronym="TESTTC"
        )
        intro_offer_section, expected_text = self._get_pertinent_intro_section(gey, self.egy)
        self.assertEqual(intro_offer_section['content'], expected_text)
        self.assertEqual(intro_offer_section['id'], 'intro-' + gey.child_branch.partial_acronym.lower())

    def test_get_intro_option_offer(self):
        gey = GroupElementYearFactory(
            parent=self.egy,
            child_branch__education_group_type__name=GroupType.OPTION_LIST_CHOICE.name
        )
        gey_option = GroupElementYearFactory(
            parent=gey.child_branch,
            child_branch__education_group_type__name=MiniTrainingType.OPTION.name,
            child_branch__partial_acronym="TESTOPTION"
        )
        intro_offer_section, expected_text = self._get_pertinent_intro_section(gey_option, self.egy)

        self.assertEqual(intro_offer_section['content'], expected_text)
        self.assertEqual(intro_offer_section['id'], 'intro-' + gey_option.child_branch.partial_acronym.lower())

    def test_get_intro_finality_offer(self):
        g = GroupElementYearFactory(
            parent=self.egy,
            child_branch__education_group_type__name=GroupType.FINALITY_120_LIST_CHOICE.name
        )
        gey = GroupElementYearFactory(
            parent=g.parent,
            child_branch__education_group_type__name=TrainingType.MASTER_MD_120.name,
            child_branch__partial_acronym="TESTFINA",
        )
        intro_offer_section, expected_text = self._get_pertinent_intro_section(gey, self.egy)
        self.assertEqual(intro_offer_section['content'], expected_text)
        self.assertEqual(intro_offer_section['id'], 'intro-' + gey.child_branch.partial_acronym.lower())

    def _get_pertinent_intro_section(self, gey, egy):
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
        annotated_egy = EducationGroupYear.objects.filter(id=egy.id).annotate(**{
            'intro-' + gey.child_branch.partial_acronym.lower(): Value(expected_text.text, output_field=CharField()),
            'intro': Value(t_label.label, output_field=CharField())
        })
        return GeneralInformationSerializer(
            annotated_egy.first(), context={
                'language': self.language,
                'acronym': egy.acronym,
                'intro_offers': [gey.child_branch.partial_acronym]
            }
        ).data['sections'][0], expected_text.text
