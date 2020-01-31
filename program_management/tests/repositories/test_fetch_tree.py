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

from base.models.enums.proposal_type import ProposalType
from base.tests.factories.group_element_year import GroupElementYearFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.prerequisite import PrerequisiteFactory
from base.tests.factories.proposal_learning_unit import ProposalLearningUnitFactory
from program_management.domain import program_tree, node, prerequisite
from program_management.models.element import Element
from program_management.tests.factories.element import ElementEducationGroupYearFactory
from program_management.repositories import fetch_tree


class TestFetchTree(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
            root_node
            |-link_level_1
              |-link_level_2
                |-- leaf
        """
        cls.root_node = ElementEducationGroupYearFactory()
        cls.link_level_1 = GroupElementYearFactory(parent=cls.root_node.education_group_year)  # TODO: Change to root_node when migration of group_element_year is done
        cls.link_level_2 = GroupElementYearFactory(
            parent=cls.link_level_1.child_branch,
            child_branch=None,
            child_leaf=LearningUnitYearFactory()
        )

    def test_case_tree_root_not_exist(self):
        unknown_tree_root_id = -1
        with self.assertRaises(Element.DoesNotExist):
            fetch_tree.fetch(unknown_tree_root_id)

    def test_case_tree_root_with_multiple_level(self):
        education_group_program_tree = fetch_tree.fetch(self.root_node.education_group_year.pk)  #  TODO: Change to root_node.group_year_id when migration of group_element_year is done
        self.assertIsInstance(education_group_program_tree, program_tree.ProgramTree)

        self.assertIsInstance(education_group_program_tree.root_node, node.NodeEducationGroupYear)
        self.assertEqual(len(education_group_program_tree.root_node.children), 1)
        self.assertEqual(
            education_group_program_tree.root_node.children[0].child.acronym,
            self.link_level_1.child_branch.acronym
        )

    def test_case_fetch_tree_leaf_have_some_prerequisites(self):
        PrerequisiteFactory(
            education_group_year=self.root_node.education_group_year,
            learning_unit_year=self.link_level_2.child_leaf,
            items__groups=(
                (
                    LearningUnitYearFactory(
                        acronym='LDROI1200', academic_year=self.link_level_2.child_leaf.academic_year
                    ),
                ),
                (
                    LearningUnitYearFactory(
                        acronym='LAGRO1600', academic_year=self.link_level_2.child_leaf.academic_year
                    ),
                    LearningUnitYearFactory(
                        acronym='LBIR2300', academic_year=self.link_level_2.child_leaf.academic_year
                    )
                )
            )
        )

        education_group_program_tree = fetch_tree.fetch(self.root_node.education_group_year.pk)
        leaf = education_group_program_tree.root_node.children[0].child.children[0].child

        self.assertIsInstance(leaf, node.NodeLearningUnitYear)
        self.assertIsInstance(leaf.prerequisite, prerequisite.Prerequisite)
        expected_str = '(LDROI1200) AND (LAGRO1600 OR LBIR2300)'
        self.assertEquals(str(leaf.prerequisite), expected_str)
        self.assertTrue(leaf.has_prerequisite)

    def test_case_fetch_tree_leaf_is_prerequisites_of(self):
        new_link = GroupElementYearFactory(
            parent=self.link_level_1.child_branch,
            child_branch=None,
            child_leaf=LearningUnitYearFactory()
        )
        # Add prerequisite between two node
        PrerequisiteFactory(
            education_group_year=self.root_node.education_group_year,
            learning_unit_year=self.link_level_2.child_leaf,
            items__groups=((new_link.child_leaf,),)
        )

        education_group_program_tree = fetch_tree.fetch(self.root_node.education_group_year.pk)
        leaf = education_group_program_tree.root_node.children[0].child.children[1].child

        self.assertIsInstance(leaf, node.NodeLearningUnitYear)
        self.assertIsInstance(leaf.is_prerequisite_of, list)
        self.assertEquals(len(leaf.is_prerequisite_of), 1)
        self.assertEquals(leaf.is_prerequisite_of[0].pk, self.link_level_2.child_leaf.pk)
        self.assertTrue(leaf.is_prerequisite)

    def test_case_fetch_tree_leaf_node_have_a_proposal(self):
        proposal_types = ProposalType.get_names()
        for p_type in proposal_types:
            proposal = ProposalLearningUnitFactory(learning_unit_year=self.link_level_2.child_leaf)
            with self.subTest(msg=p_type):
                proposal.type = p_type
                proposal.save()

                education_group_program_tree = fetch_tree.fetch(self.root_node.education_group_year.pk)
                leaf = education_group_program_tree.root_node.children[0].child.children[0].child
                self.assertTrue(leaf.has_proposal)
                self.assertEquals(leaf.proposal_type, p_type)

    def test_case_fetch_tree_leaf_node_have_no_proposal(self):
        education_group_program_tree = fetch_tree.fetch(self.root_node.education_group_year.pk)
        leaf = education_group_program_tree.root_node.children[0].child.children[0].child
        self.assertFalse(leaf.has_proposal)
        self.assertIsNone(leaf.proposal_type)