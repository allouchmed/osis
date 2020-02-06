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
from django.conf import settings
from django.test import TestCase

from base.models.admission_condition import AdmissionCondition
from base.models.education_group_year import EducationGroupYear
from base.models.enums.education_group_types import TrainingType
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.admission_condition import AdmissionConditionFactory
from base.tests.factories.education_group_publication_contact import EducationGroupPublicationContactFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory, EducationGroupYearCommonMasterFactory, \
    TrainingFactory, EducationGroupYearCommonFactory
from cms.enums.entity_name import OFFER_YEAR
from cms.tests.factories.translated_text import TranslatedTextFactory
from cms.tests.factories.translated_text_label import TranslatedTextLabelFactory
from webservices.api.serializers.section import SectionSerializer, AchievementSectionSerializer, \
    AdmissionConditionSectionSerializer, ContactsSectionSerializer, EvaluationSectionSerializer
from webservices.business import SKILLS_AND_ACHIEVEMENTS_INTRO, SKILLS_AND_ACHIEVEMENTS_EXTRA, EVALUATION_KEY


class SectionSerializerTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.data_to_serialize = {
            'label': 'LABEL',
            'translated_label': 'TRANSLATED_LABEL',
            'text': 'TEXT',
            'dummy': 'DUMMY'
        }
        cls.serializer = SectionSerializer(cls.data_to_serialize)

    def test_contains_expected_fields(self):
        expected_fields = [
            'id',
            'label',
            'content'
        ]
        self.assertListEqual(list(self.serializer.data.keys()), expected_fields)

    def test_contains_expected_fields_with_free_text(self):
        self.data_to_serialize['free_text'] = 'FREE_TEXT'
        serializer = SectionSerializer(self.data_to_serialize)
        expected_fields = [
            'id',
            'label',
            'content',
        ]
        self.assertListEqual(list(serializer.data.keys()), expected_fields)


class AchievementSectionSerializerTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.data_to_serialize = {
            'id': 'ID',
            'dummy': 'DUMMY'
        }
        cls.language = settings.LANGUAGE_CODE_EN
        cls.egy = EducationGroupYearFactory()
        for label in [SKILLS_AND_ACHIEVEMENTS_INTRO, SKILLS_AND_ACHIEVEMENTS_EXTRA]:
            TranslatedTextFactory(
                text_label__label=label,
                reference=cls.egy.id,
                entity=OFFER_YEAR,
                language=cls.language
            )
        cls.serializer = AchievementSectionSerializer(cls.data_to_serialize, context={
            'egy': cls.egy,
            'lang': cls.language
        })

    def test_contains_expected_fields(self):
        expected_fields = [
            'id',
            'label',
            'content'
        ]
        self.assertListEqual(list(self.serializer.data.keys()), expected_fields)


class AdmissionConditionSectionSerializerTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.data_to_serialize = {
            'id': 'ID',
            'dummy': 'DUMMY'
        }
        cls.language = settings.LANGUAGE_CODE_EN
        cls.egy = EducationGroupYearFactory(
            acronym='ARKE2M',
            education_group_type__name=TrainingType.PGRM_MASTER_120.name
        )
        common_egy = EducationGroupYearCommonMasterFactory(academic_year=cls.egy.academic_year)
        AdmissionConditionFactory(education_group_year=common_egy)
        AdmissionConditionFactory(education_group_year=cls.egy)
        cls.serializer = AdmissionConditionSectionSerializer(cls.data_to_serialize, context={
            'egy': cls.egy,
            'lang': cls.language
        })

    def test_contains_expected_fields(self):
        expected_fields = [
            'id',
            'label',
            'content'
        ]
        self.assertListEqual(list(self.serializer.data.keys()), expected_fields)

    def test_ensure_get_education_group_year(self):
        self.assertIsInstance(self.serializer.get_education_group_year(), EducationGroupYear)
        self.assertEqual(self.serializer.get_education_group_year(), self.egy)

    def test_ensure_admission_condition_is_created_if_not_exists(self):
        training_wihtout_admission_condition = TrainingFactory(education_group_type__name=TrainingType.BACHELOR.name)

        serializer = AdmissionConditionSectionSerializer({}, context={
            'egy': training_wihtout_admission_condition,
            'lang': self.language
        })

        new_instance = serializer.get_admission_condition()
        self.assertIsInstance(new_instance, AdmissionCondition)
        self.assertEqual(new_instance.education_group_year_id, training_wihtout_admission_condition.pk)


class ContactsSectionSerializerTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.data_to_serialize = {
            'id': 'ID',
            'dummy': 'DUMMY'
        }
        cls.language = 'en'
        cls.egy = EducationGroupYearFactory()
        EducationGroupPublicationContactFactory(education_group_year=cls.egy)
        cls.serializer = ContactsSectionSerializer(cls.data_to_serialize, context={
            'egy': cls.egy,
            'lang': cls.language
        })

    def test_contains_expected_fields(self):
        expected_fields = [
            'id',
            'label',
            'content'
        ]
        self.assertListEqual(list(self.serializer.data.keys()), expected_fields)


class EvaluationSectionSerializerTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.academic_year = AcademicYearFactory(current=True)
        cls.common_egy = EducationGroupYearCommonFactory(academic_year=cls.academic_year)
        cls.language = settings.LANGUAGE_CODE_EN
        TranslatedTextLabelFactory(
            language=cls.language,
            text_label__label=EVALUATION_KEY
        )
        TranslatedTextFactory(
            reference=cls.common_egy.id,
            entity=OFFER_YEAR,
            language=cls.language,
            text_label__label=EVALUATION_KEY,
            text="EVALUATION_TEXT_COMMON"
        )

    def test_get_both_evaluation_texts(self):
        egy = TrainingFactory(
            education_group_type__name=TrainingType.PGRM_MASTER_120.name,
            academic_year=self.academic_year
        )
        TranslatedTextFactory(
            reference=egy.id,
            entity=OFFER_YEAR,
            language=self.language,
            text_label__label=EVALUATION_KEY,
            text=EVALUATION_KEY.upper() + "_TEXT"
        )

        serializer = EvaluationSectionSerializer(
            {'id': EVALUATION_KEY}, context={'egy': egy, 'lang': self.language}
        ).data
        self.assertEqual(serializer['content'], 'EVALUATION_TEXT_COMMON')
        self.assertEqual(serializer['free_text'], 'EVALUATION_TEXT')

    def test_get_only_specific_evaluation_for_iufc_offers(self):
        egy = EducationGroupYearFactory(
            education_group_type__name=TrainingType.UNIVERSITY_FIRST_CYCLE_CERTIFICATE.name,
            academic_year=self.academic_year,
            acronym='TEST1FC'
        )
        TranslatedTextFactory(
            reference=egy.id,
            text_label__label=EVALUATION_KEY,
            language=self.language,
            text='EVALUATION_TEXT_FC'
        )
        serializer = EvaluationSectionSerializer(
            {'id': EVALUATION_KEY}, context={'egy': egy, 'lang': self.language}
        ).data
        self.assertIsNone(serializer['content'])
        self.assertEqual(serializer['free_text'], 'EVALUATION_TEXT_FC')
