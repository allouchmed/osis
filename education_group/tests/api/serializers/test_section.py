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
from django.test import TestCase

from base.tests.factories.education_group_year import EducationGroupYearFactory
from cms.enums.entity_name import OFFER_YEAR
from cms.tests.factories.translated_text import TranslatedTextFactory
from education_group.api.serializers.section import SectionSerializer, AchievementSectionSerializer
from webservices.business import SKILLS_AND_ACHIEVEMENTS_INTRO, SKILLS_AND_ACHIEVEMENTS_EXTRA


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
            'free_text'
        ]
        self.assertListEqual(list(serializer.data.keys()), expected_fields)


class AchievementSectionSerializerTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.data_to_serialize = {
            'id': 'ID',
            'dummy': 'DUMMY'
        }
        cls.language = 'en'
        cls.egy = EducationGroupYearFactory()
        TranslatedTextFactory(
            text_label__label=SKILLS_AND_ACHIEVEMENTS_INTRO,
            reference=cls.egy.id,
            entity=OFFER_YEAR,
            language=cls.language
        )
        TranslatedTextFactory(
            text_label__label=SKILLS_AND_ACHIEVEMENTS_EXTRA,
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