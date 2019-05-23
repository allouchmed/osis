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
import datetime

import base.models.learning_container_year
from base.models import entity_container_year
from base.models.enums import entity_container_year_link_type
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.entity import EntityFactory
from base.tests.factories.entity_version import EntityVersionFactory
from base.tests.factories.learning_container_year import LearningContainerYearFactory
from base.tests.factories.entity_container_year import EntityContainerYearFactory


class EntityContainerYearTest(TestCase):
    def setUp(self):
        self.entity = EntityFactory()
        self.entity_versions = {}
        self.academic_years = {}
        for year in [2015, 2016]:
            self.academic_years[year] = AcademicYearFactory(year=year)
            self.entity_versions[year] = EntityVersionFactory(entity=self.entity,
                                                              parent=None,
                                                              acronym="Entity V_{}".format(year),
                                                              start_date=datetime.datetime(year, 1, 1),
                                                              end_date=datetime.datetime(year, 12, 30))

    def test_find_entities_no_values(self):
        l_container_year = LearningContainerYearFactory(
            academic_year=self.academic_years[2015],
            requirement_entity=None
        )
        # No link between an entity/learning_container_year, so no result
        no_entity = base.models.learning_container_year.find_last_entity_version_grouped_by_linktypes(
            learning_container_year=l_container_year)
        self.assertFalse(no_entity)

    def test_find_entities_with_empty_link_type(self):
        l_container_year = LearningContainerYearFactory(
            academic_year=self.academic_years[2015],
            requirement_entity=self.entity,
        )
        # No link between an entity/learning_container_year, so no result
        no_entity = base.models.learning_container_year.find_last_entity_version_grouped_by_linktypes(
            learning_container_year=l_container_year, link_type=[])
        self.assertFalse(no_entity)

    def test_find_entities(self):
        work_on_year = 2015

        l_container_year = LearningContainerYearFactory(
            academic_year=self.academic_years[work_on_year],
            requirement_entity=self.entity,
            allocation_entity=self.entity,
        )
        # Find all entities
        entities = base.models.learning_container_year.find_last_entity_version_grouped_by_linktypes(
            learning_container_year=l_container_year)
        self.assertIsInstance(entities, dict)
        self.assertTrue(entity_container_year_link_type.REQUIREMENT_ENTITY in entities)
        self.assertTrue(entity_container_year_link_type.ALLOCATION_ENTITY in entities)
        self.assertFalse(entity_container_year_link_type.ADDITIONAL_REQUIREMENT_ENTITY_1 in entities)
        self.assertFalse(entity_container_year_link_type.ADDITIONAL_REQUIREMENT_ENTITY_2 in entities)

    def test_find_entities_grouped_by_linktype(self):
        a_learning_container_year = LearningContainerYearFactory()

        requirement_entity = EntityFactory()
        EntityContainerYearFactory(learning_container_year=a_learning_container_year,
                                   entity=requirement_entity,
                                   type=entity_container_year_link_type.REQUIREMENT_ENTITY)

        allocation_entity = EntityFactory()
        EntityContainerYearFactory(learning_container_year=a_learning_container_year,
                                   entity=allocation_entity,
                                   type=entity_container_year_link_type.ALLOCATION_ENTITY)

        additional_requirement_entity_1 = EntityFactory()
        EntityContainerYearFactory(learning_container_year=a_learning_container_year,
                                   entity=additional_requirement_entity_1,
                                   type=entity_container_year_link_type.ADDITIONAL_REQUIREMENT_ENTITY_1)

        additional_requirement_entity_2 = EntityFactory()
        EntityContainerYearFactory(learning_container_year=a_learning_container_year,
                                   entity=additional_requirement_entity_2,
                                   type=entity_container_year_link_type.ADDITIONAL_REQUIREMENT_ENTITY_2)

        entities_by_linktype = entity_container_year.find_entities_grouped_by_linktype(a_learning_container_year)

        expected_result = {
            entity_container_year_link_type.REQUIREMENT_ENTITY: requirement_entity,
            entity_container_year_link_type.ALLOCATION_ENTITY: allocation_entity,
            entity_container_year_link_type.ADDITIONAL_REQUIREMENT_ENTITY_1: additional_requirement_entity_1,
            entity_container_year_link_type.ADDITIONAL_REQUIREMENT_ENTITY_2: additional_requirement_entity_2
        }

        self.assertDictEqual(entities_by_linktype, expected_result)

    def test_find_by_learning_container_year_and_linktype(self):
        a_learning_container_year = LearningContainerYearFactory()
        expected_container = EntityContainerYearFactory(learning_container_year=a_learning_container_year,
                                                        type=entity_container_year_link_type.REQUIREMENT_ENTITY)

        returned_container = entity_container_year.find_by_learning_container_year_and_linktype(
            a_learning_container_year, entity_container_year_link_type.REQUIREMENT_ENTITY
        )

        self.assertEqual(expected_container, returned_container)
