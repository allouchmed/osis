##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2020 Université catholique de Louvain (http://www.uclouvain.be)
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

from program_management.ddd.domain.node import NodeGroupYear, NodeLearningUnitYear
from program_management.tests.ddd.factories.node import NodeGroupYearFactory, NodeLearningUnitYearFactory


class TestAddChildNode(TestCase):
    def test_add_child_to_node(self):
        group_year_node = NodeGroupYear(0, "LDROI200G", "Tronc commun", 2018)
        learning_unit_year_node = NodeLearningUnitYear(2, "LDROI100", "Introduction", 2018)

        group_year_node.add_child(learning_unit_year_node, relative_credits=5, comment='Dummy comment')
        self.assertEquals(len(group_year_node.children), 1)

        self.assertEquals(group_year_node.children[0].relative_credits, 5)
        self.assertEquals(group_year_node.children[0].comment, 'Dummy comment')


class TestDescendentsPropertyNode(TestCase):
    def setUp(self):
        self.root_node = NodeGroupYear(0, "LDROI200T", "Tronc commun", 2018)
        self.subgroup_node = NodeGroupYear(1, "LDROI200G", "Sub group", 2018)
        self.leaf = NodeLearningUnitYear(2, "LDROI100", "Introduction", 2018)

    def test_case_no_descendents(self):
        self.assertIsInstance(self.root_node.descendents, dict)
        self.assertEquals(self.root_node.descendents, {})

    def test_case_all_descendents_with_path_as_key(self):
        self.subgroup_node.add_child(self.leaf)
        self.root_node.add_child(self.subgroup_node)

        self.assertIsInstance(self.root_node.descendents, dict)
        expected_keys = [
            "|".join([str(self.root_node.pk), str(self.subgroup_node.pk)]),   # First level
            "|".join([str(self.root_node.pk), str(self.subgroup_node.pk), str(self.leaf.pk)]),  # Second level
        ]
        self.assertTrue(all(k in expected_keys for k in self.root_node.descendents.keys()))


class TestEq(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.node_id = 1
        cls.node = NodeGroupYearFactory(node_id=1)

    def test_when_nodes_group_year_are_equal(self):
        node_with_same_id = NodeGroupYearFactory(node_id=self.node_id)
        self.assertTrue(self.node == node_with_same_id)

    def test_when_nodes_group_year_are_not_equal(self):
        node_with_different_id = NodeGroupYearFactory(node_id=self.node_id + 1)
        self.assertFalse(self.node == node_with_different_id)

    def test_when_nodes_learning_unit_are_equal(self):
        node_with_same_id = NodeLearningUnitYearFactory(node_id=self.node_id)
        self.assertTrue(self.node == node_with_same_id)

    def test_when_nodes_learning_unit_are_not_equal(self):
        node_with_different_id = NodeLearningUnitYearFactory(node_id=self.node_id + 1)
        self.assertFalse(self.node == node_with_different_id)


class TestStr(TestCase):
    @classmethod
    def setUpTestData(cls):
        acronym = 'Acronym'
        year = 2019
        cls.node_group_year = NodeGroupYearFactory(acronym=acronym, year=year)
        cls.node_learning_unit = NodeLearningUnitYearFactory(acronym=acronym, year=year)

    def test_node_group_year_str(self):
        self.assertEqual(str(self.node_group_year), 'Acronym (2019)')

    def test_node_learning_unit_str(self):
        self.assertEqual(str(self.node_learning_unit), 'Acronym (2019)')
