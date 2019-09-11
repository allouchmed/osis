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
from django.db.models import F
from django.test import TestCase

from attribution.models.attribution_charge_new import AttributionChargeNew
from attribution.tests.factories.attribution_charge_new import AttributionChargeNewFactory
from base.tests.factories.person import PersonFactory
from learning_unit.api.serializers.attribution import PersonAttributionSerializer, LearningUnitAttributionSerializer


class PersonAttributionSerializerTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.person = PersonFactory()
        cls.serializer = PersonAttributionSerializer(cls.person)

    def test_contains_expected_fields(self):
        expected_fields = [
            'first_name',
            'middle_name',
            'last_name',
            'email',
            'global_id'
        ]
        self.assertListEqual(list(self.serializer.data.keys()), expected_fields)


class LearningUnitAttributionSerializerTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.attrib = AttributionChargeNewFactory()
        cls.attribution = AttributionChargeNew.objects.annotate(
            first_name=F('attribution__tutor__person__first_name'),
            middle_name=F('attribution__tutor__person__middle_name'),
            last_name=F('attribution__tutor__person__last_name'),
            email=F('attribution__tutor__person__email'),
            global_id=F('attribution__tutor__person__global_id'),
        ).get(id=cls.attrib.id)

        cls.serializer = LearningUnitAttributionSerializer(cls.attribution)

    def test_contains_expected_fields(self):
        attribution = AttributionChargeNew.objects.annotate(
            first_name=F('attribution__tutor__person__first_name'),
            middle_name=F('attribution__tutor__person__middle_name'),
            last_name=F('attribution__tutor__person__last_name'),
            email=F('attribution__tutor__person__email'),
            global_id=F('attribution__tutor__person__global_id'),
        ).get(id=self.attrib.id)

        serializer = LearningUnitAttributionSerializer(attribution)
        expected_fields = [
            'first_name',
            'middle_name',
            'last_name',
            'email',
            'global_id',
            'function',
            'function_text',
            'substitute'
        ]
        self.assertListEqual(list(serializer.data.keys()), expected_fields)
