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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################

from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.test.utils import override_settings
from django.contrib.auth.models import Permission

from base.business.learning_units.perms import MSG_EXISTING_PROPOSAL_IN_EPC, MSG_NO_ELIGIBLE_TO_MODIFY_END_DATE, \
    MSG_CAN_EDIT_PROPOSAL_NO_LINK_TO_ENTITY, \
    MSG_NOT_PROPOSAL_STATE_FACULTY, MSG_NOT_ELIGIBLE_TO_EDIT_PROPOSAL, \
    MSG_PERSON_NOT_IN_ACCORDANCE_WITH_PROPOSAL_STATE, MSG_ONLY_IF_YOUR_ARE_LINK_TO_ENTITY, MSG_NOT_GOOD_RANGE_OF_YEARS, \
    MSG_NO_RIGHTS_TO_CONSOLIDATE, \
    MSG_NOT_ELIGIBLE_TO_CONSOLIDATE_PROPOSAL, MSG_PROPOSAL_NOT_IN_CONSOLIDATION_ELIGIBLE_STATES, \
    MSG_NOT_ELIGIBLE_TO_DELETE_LU, MSG_CAN_DELETE_ACCORDING_TO_TYPE, MSG_PROPOSAL_IS_ON_AN_OTHER_YEAR, \
    can_modify_end_year_by_proposal, is_eligible_to_modify_by_proposal, can_modify_by_proposal, \
    MSG_NOT_ELIGIBLE_TO_MODIFY_END_YEAR_PROPOSAL_ON_THIS_YEAR, MSG_NOT_ELIGIBLE_TO_PUT_IN_PROPOSAL_ON_THIS_YEAR
from base.templatetags.learning_unit_li import li_edit_lu, li_edit_date_lu, li_modification_proposal, is_valid_proposal, \
    MSG_IS_NOT_A_PROPOSAL, MSG_PROPOSAL_NOT_ON_CURRENT_LU, DISABLED, li_suppression_proposal, li_cancel_proposal, \
    li_edit_proposal, li_consolidate_proposal, li_delete_all_lu
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.learning_unit import LearningUnitFactory
from base.tests.factories.learning_container_year import LearningContainerYearFactory
from base.tests.factories.person import CentralManagerFactory, FacultyManagerFactory
from base.tests.factories.proposal_learning_unit import ProposalLearningUnitFactory
from base.tests.factories.academic_year import create_current_academic_year, AcademicYearFactory
from base.models.enums import learning_unit_year_subtypes
from base.tests.factories.user import UserFactory
from base.tests.factories.person import PersonFactory
from base.tests.factories.person_entity import PersonEntityFactory
from base.tests.factories.entity_container_year import EntityContainerYearFactory
from base.models.enums import entity_container_year_link_type
from base.models.enums import learning_container_year_types
from base.models.enums.proposal_state import ProposalState
from django.conf import settings
from django.core.exceptions import PermissionDenied

ID_LINK_EDIT_LU = "link_edit_lu"
ID_LINK_EDIT_DATE_LU = "link_edit_date_lu"


@override_settings(LANGUAGES=[('en', 'English'), ], LANGUAGE_CODE='en')
class LearningUnitTagLiEditTest(TestCase):

    def setUp(self):
        self.learning_unit = LearningUnitFactory()
        self.previous_learning_unit = LearningUnitFactory(existing_proposal_in_epc=False)
        self.current_academic_year = create_current_academic_year()
        self.previous_academic_year = AcademicYearFactory(year=self.current_academic_year.year - 1)
        self.next_academic_yr = AcademicYearFactory(year=self.current_academic_year.year + 1)
        AcademicYearFactory(year=self.current_academic_year.year + 2)
        AcademicYearFactory(year=self.current_academic_year.year + 3)
        AcademicYearFactory(year=self.current_academic_year.year + 4)
        self.later_academic_year = AcademicYearFactory(year=self.current_academic_year.year + 5)
        self.lcy = LearningContainerYearFactory(academic_year=self.next_academic_yr,
                                                container_type=learning_container_year_types.COURSE)
        self.learning_unit_year = LearningUnitYearFactory(
            academic_year=self.next_academic_yr,
            subtype=learning_unit_year_subtypes.FULL,
            learning_unit=self.learning_unit,
            learning_container_year=self.lcy
        )
        self.previous_learning_unit_year = LearningUnitYearFactory(
            academic_year=self.previous_academic_year,
            learning_unit=self.learning_unit
        )

        self.previous_luy_2 = LearningUnitYearFactory(
            academic_year=self.previous_academic_year,
            subtype=learning_unit_year_subtypes.FULL,
            learning_unit=self.previous_learning_unit,
            learning_container_year=LearningContainerYearFactory(academic_year=self.previous_academic_year,
                                                                 container_type=learning_container_year_types.COURSE)
        )

        self.previous_proposal = ProposalLearningUnitFactory(learning_unit_year=self.previous_luy_2)
        self.user = UserFactory()
        self.central_manager_person = CentralManagerFactory()
        self.person_entity = PersonEntityFactory(person=self.central_manager_person)

        self.requirement_entity = self.person_entity.entity
        self.proposal = ProposalLearningUnitFactory(
            learning_unit_year=self.learning_unit_year,
            initial_data={
                'learning_container_year': {'common_title': self.lcy.common_title},
                'entities': {'REQUIREMENT_ENTITY': self.requirement_entity.id}
            },
        )

        self.entity_container_yr = EntityContainerYearFactory(
            learning_container_year=self.learning_unit_year.learning_container_year,
            entity=self.person_entity.entity,
            type=entity_container_year_link_type.REQUIREMENT_ENTITY
        )
        EntityContainerYearFactory(
            learning_container_year=self.previous_learning_unit_year.learning_container_year,
            entity=self.person_entity.entity,
            type=entity_container_year_link_type.REQUIREMENT_ENTITY
        )
        self.client.force_login(user=self.central_manager_person.user)
        self.url_edit = reverse('edit_learning_unit', args=[self.learning_unit_year.id])
        self.request = RequestFactory().get("")
        self.context = {
            "learning_unit_year": self.learning_unit_year,
            "request": self.request,
            "user": self.central_manager_person.user,
            "proposal": self.proposal
        }

    @override_settings(YEAR_LIMIT_LUE_MODIFICATION=2018)
    def test_li_edit_lu_year_non_editable_for_faculty_manager(self):
        faculty_manager = FacultyManagerFactory()

        self.context["learning_unit_year"] = self.previous_learning_unit_year
        self.context["user"] = faculty_manager.user

        result = li_edit_lu(self.context, self.url_edit, "")

        self.assertEqual(
            result, {
                'load_modal': False,
                'id_li': ID_LINK_EDIT_LU,
                'url': "#",
                'title': "{}.  {}".format("You can't modify learning unit under year : %(year)d" %
                                          {"year": settings.YEAR_LIMIT_LUE_MODIFICATION},
                                          "Modifications should be made in EPC for year %(year)d" %
                                          {"year": self.previous_learning_unit_year.academic_year.year}),
                'class_li': DISABLED,
                'text': "",
                'data_target': ""
            })

    def test_li_edit_lu_year_is_editable_but_existing_proposal_in_epc(self):
        self.learning_unit.existing_proposal_in_epc = True
        self.learning_unit.save()
        self.context["learning_unit_year"] = self.learning_unit_year

        result = li_edit_lu(self.context, self.url_edit, "")
        self.assertEqual(result,
                         self._get_result_data_expected(ID_LINK_EDIT_LU, MSG_EXISTING_PROPOSAL_IN_EPC))

        result = li_edit_date_lu(self.context, self.url_edit, "")
        self.assertEqual(
            result,
            self._get_result_data_expected(ID_LINK_EDIT_DATE_LU, MSG_EXISTING_PROPOSAL_IN_EPC))

        result = li_delete_all_lu(self.context, self.url_edit, '', "#modalDeleteLuy")
        expected = self._get_result_data_expected_delete("link_delete_lus", MSG_EXISTING_PROPOSAL_IN_EPC)

        self.assertEqual(result, expected)

        self.proposal.learning_unit_year = self.learning_unit_year
        self.proposal.save()
        self.context["proposal"] = self.proposal
        result = li_suppression_proposal(self.context, self.url_edit, "")
        self.assertEqual(
            result, self._get_result_data_expected_for_proposal_suppression("link_proposal_suppression",
                                                                            MSG_EXISTING_PROPOSAL_IN_EPC,
                                                                            DISABLED
                                                                            )
        )
        result = li_modification_proposal(self.context, self.url_edit, "")

        self.assertEqual(
            result, self._get_result_data_expected("link_proposal_modification", MSG_EXISTING_PROPOSAL_IN_EPC, )
        )

    def test_li_edit_lu_year_is_learning_unit_year_not_in_range_to_be_modified(self):
        person_faculty = FacultyManagerFactory()
        later_luy = LearningUnitYearFactory(academic_year=self.later_academic_year,
                                            learning_unit=LearningUnitFactory(existing_proposal_in_epc=False))
        self.context["learning_unit_year"] = later_luy
        self.context["user"] = person_faculty.user

        result = li_edit_lu(self.context, reverse('edit_learning_unit', args=[later_luy.id]), "")

        self.assertEqual(
            result, self._get_result_data_expected(ID_LINK_EDIT_LU,
                                                   MSG_NOT_GOOD_RANGE_OF_YEARS
                                                   )
        )

    def test_li_edit_lu_year_person_is_not_linked_to_entity_in_charge_of_lu(self):
        a_person = CentralManagerFactory()
        self.context['user'] = a_person.user
        result = li_edit_lu(self.context, self.url_edit, "")
        self.assertEqual(
            result, self._get_result_data_expected(ID_LINK_EDIT_LU,
                                                   MSG_ONLY_IF_YOUR_ARE_LINK_TO_ENTITY
                                                   )
        )

    def test_li_edit_lu_everything_ok(self):
        self.proposal.delete()
        result = li_edit_lu(self.context, self.url_edit, "")
        self.assertEqual(
            result, self._get_result_data_expected(ID_LINK_EDIT_LU, url=self.url_edit)
        )

        result = li_edit_date_lu(self.context, self.url_edit, "")

        self.assertEqual(
            result, self._get_result_data_expected(ID_LINK_EDIT_DATE_LU, url=self.url_edit)
        )

    def test_li_edit_date_person_test_is_eligible_to_modify_end_date_based_on_container_type(self):
        lu = LearningUnitFactory(existing_proposal_in_epc=False)
        learning_unit_year_without_proposal = LearningUnitYearFactory(
            academic_year=self.current_academic_year,
            subtype=learning_unit_year_subtypes.FULL,
            learning_unit=lu,
            learning_container_year=self.lcy
        )
        person_faculty_manager = FacultyManagerFactory()

        PersonEntityFactory(person=person_faculty_manager,
                            entity=self.entity_container_yr.entity)

        self.context['user'] = person_faculty_manager.user
        self.context['learning_unit_year'] = learning_unit_year_without_proposal
        result = li_edit_date_lu(self.context, self.url_edit, "")

        self.assertEqual(
            result, self._get_result_data_expected(ID_LINK_EDIT_DATE_LU, MSG_NO_ELIGIBLE_TO_MODIFY_END_DATE)
        )

        # allowed if _is_person_central_manager or
        #            _is_learning_unit_year_a_partim or
        #            negation(_is_container_type_course_dissertation_or_internship),
        # test 1st condition true
        self.context['user'] = self.central_manager_person.user
        result = li_edit_date_lu(self.context, self.url_edit, "")

        self.assertEqual(
            result, self._get_result_data_expected(ID_LINK_EDIT_DATE_LU, url=self.url_edit)
        )
        # test 2nd condition true
        self.context['user'] = person_faculty_manager.user
        learning_unit_year_without_proposal.subtype = learning_unit_year_subtypes.PARTIM
        learning_unit_year_without_proposal.save()
        self.context['learning_unit_year'] = learning_unit_year_without_proposal

        self.assertEqual(li_edit_date_lu(self.context, self.url_edit, ""),
                         self._get_result_data_expected(ID_LINK_EDIT_DATE_LU, url=self.url_edit))
        # test 3rd condition true
        learning_unit_year_without_proposal.learning_container_year.container_type = learning_container_year_types.OTHER_COLLECTIVE
        learning_unit_year_without_proposal.learning_container_year.save()
        learning_unit_year_without_proposal.subtype = learning_unit_year_subtypes.FULL
        learning_unit_year_without_proposal.save()
        self.context['learning_unit_year'] = learning_unit_year_without_proposal

        self.assertEqual(li_edit_date_lu(self.context, self.url_edit, ""),
                         self._get_result_data_expected(ID_LINK_EDIT_DATE_LU, url=self.url_edit))

    def test_is_not_valid_not_proposal(self):
        self.context['proposal'] = None
        permission_denied_message, disabled = is_valid_proposal(self.context)
        self.assertEqual(permission_denied_message, MSG_IS_NOT_A_PROPOSAL)
        self.assertEqual(disabled, DISABLED)

    def test_is_not_valid_not_same_lu(self):
        self.context['learning_unit_year'] = self.previous_learning_unit_year
        self.context['proposal'] = self.proposal

        permission_denied_message, disabled = is_valid_proposal(self.context)
        self.assertEqual(permission_denied_message, MSG_PROPOSAL_NOT_ON_CURRENT_LU)
        self.assertEqual(disabled, DISABLED)

    def test_is_valid(self):
        self.context['learning_unit_year'] = self.learning_unit_year
        self.context['proposal'] = self.proposal

        permission_denied_message, disabled = is_valid_proposal(self.context)
        self.assertEqual(permission_denied_message, "")
        self.assertEqual(disabled, "")

    @override_settings(YEAR_LIMIT_LUE_MODIFICATION=2018)
    def test_li_edit_proposal_as_faculty_manager(self):
        person_faculty_manager = FacultyManagerFactory()
        self.context['user'] = person_faculty_manager.user

        self.context['proposal'] = self.proposal
        self.context['learning_unit_year'] = self.proposal.learning_unit_year

        result = li_edit_proposal(self.context, self.url_edit, "")
        self.assertEqual(
            result,
            self._get_result_data_expected_for_proposal('link_proposal_edit', MSG_CAN_EDIT_PROPOSAL_NO_LINK_TO_ENTITY,
                                                        DISABLED))

        faculty_manager_person = FacultyManagerFactory()
        PersonEntityFactory(person=faculty_manager_person,
                            entity=self.requirement_entity)
        self.context['user'] = faculty_manager_person.user
        self.context['person'] = faculty_manager_person
        self.proposal.state = ProposalState.CENTRAL.name
        self.proposal.save()
        self.context['proposal'] = self.proposal
        result = li_edit_proposal(self.context, self.url_edit, "")
        self.assertEqual(
            result,
            self._get_result_data_expected_for_proposal('link_proposal_edit', MSG_NOT_PROPOSAL_STATE_FACULTY, DISABLED))

        self.proposal.state = ProposalState.FACULTY.name
        self.proposal.save()
        self.context['proposal'] = self.proposal
        result = li_edit_proposal(self.context, self.url_edit, "")
        self.assertEqual(
            result,
            self._get_result_data_expected_for_proposal('link_proposal_edit', MSG_NOT_ELIGIBLE_TO_EDIT_PROPOSAL,
                                                        DISABLED)
        )

    def test_li_cancel_proposal_not_accordance_with_proposal_state(self):
        person_faculty_manager = FacultyManagerFactory()
        self.context['user'] = person_faculty_manager.user
        self.proposal.state = ProposalState.CENTRAL.name
        self.proposal.save()
        self.context['proposal'] = self.proposal
        result = li_cancel_proposal(self.context, self.url_edit, "")
        self.assertEqual(result,
                         self._get_result_data_expected_for_proposal('link_cancel_proposal',
                                                                     MSG_PERSON_NOT_IN_ACCORDANCE_WITH_PROPOSAL_STATE,
                                                                     DISABLED)
                         )
        self.proposal.state = ProposalState.FACULTY.name
        self.proposal.save()
        result = li_cancel_proposal(self.context, self.url_edit, "")
        self.assertEqual(result,
                         self._get_result_data_expected_for_proposal('link_cancel_proposal',
                                                                     MSG_CAN_EDIT_PROPOSAL_NO_LINK_TO_ENTITY, DISABLED))

    def test_li_consolidate_proposal_no_rights_to_consolidate(self):
        person = PersonFactory()
        self.context['user'] = person.user
        result = li_consolidate_proposal(self.context, self.url_edit, "")
        self.assertEqual(result,
                         self._get_result_data_expected_for_proposal('link_consolidate_proposal',
                                                                     MSG_NO_RIGHTS_TO_CONSOLIDATE, DISABLED))

    def test_li_consolidate_proposal_not_good_proposal_state(self):
        self.context['user'] = self._build_user_with_permission_to_consolidate()
        self.proposal.state = ProposalState.SUSPENDED.name
        self.proposal.save()
        self.context['proposal'] = self.proposal
        result = li_consolidate_proposal(self.context, self.url_edit, "")
        self.assertEqual(result,
                         self._get_result_data_expected_for_proposal('link_consolidate_proposal',
                                                                     MSG_PROPOSAL_NOT_IN_CONSOLIDATION_ELIGIBLE_STATES,
                                                                     DISABLED))

    def test_li_consolidate_proposal_not_attached_to_entity(self):
        self.context['user'] = self._build_user_with_permission_to_consolidate()
        self.proposal.state = ProposalState.ACCEPTED.name
        self.proposal.save()
        self.context['proposal'] = self.proposal
        result = li_consolidate_proposal(self.context, self.url_edit, "")
        self.assertEqual(result,
                         self._get_result_data_expected_for_proposal('link_consolidate_proposal',
                                                                     MSG_CAN_EDIT_PROPOSAL_NO_LINK_TO_ENTITY, DISABLED))

    def test_li_consolidate_proposal(self):
        self.central_manager_person.user.user_permissions \
            .add(Permission.objects.get(codename="can_consolidate_learningunit_proposal"))
        self.context['user'] = self.central_manager_person.user
        self.proposal.state = ProposalState.ACCEPTED.name
        self.proposal.save()
        self.context['proposal'] = self.proposal
        result = li_consolidate_proposal(self.context, self.url_edit, "")
        self.assertEqual(result,
                         self._get_result_data_expected_for_proposal('link_consolidate_proposal', "", ""))

    def test_li_delete_all_lu_cannot_delete_learning_unit_year_according_type(self):
        self.context['user'] = FacultyManagerFactory().user

        lcy_master = LearningContainerYearFactory(academic_year=self.current_academic_year,
                                                  container_type=learning_container_year_types.COURSE)
        learning_unit_yr = LearningUnitYearFactory(
            academic_year=self.current_academic_year,
            subtype=learning_unit_year_subtypes.FULL,
            learning_unit=LearningUnitFactory(),
            learning_container_year=lcy_master
        )
        self.context['learning_unit_year'] = learning_unit_yr

        result = li_delete_all_lu(self.context, self.url_edit, '', "#modalDeleteLuy")
        expected = self._get_result_data_expected_delete("link_delete_lus", MSG_CAN_DELETE_ACCORDING_TO_TYPE)

        self.assertEqual(result, expected)

    def test_li_delete_all_lu_everything_ok(self):
        result = li_delete_all_lu(self.context, self.url_edit, '', "#modalDeleteLuy")

        expected = {
            'class_li': 'disabled',
            'load_modal': False,
            'url': '#',
            'id_li': 'link_delete_lus',
            'title': "Vous ne pouvez pas supprimer une unité d'enseignement existant avant 2018",
            'text': '',
            'data_target': ''
        }

        self.assertEqual(result, expected)

    def test_can_modify_end_year_by_proposal_undefined_group(self):
        faculty_no_faculty_no_central = PersonFactory()
        lcy = LearningContainerYearFactory(academic_year=self.previous_academic_year,
                                           container_type=learning_container_year_types.COURSE)
        learning_unit_yr = LearningUnitYearFactory(
            academic_year=self.previous_academic_year,
            subtype=learning_unit_year_subtypes.FULL,
            learning_unit=LearningUnitFactory(),
            learning_container_year=lcy
        )

        self.assertFalse(can_modify_end_year_by_proposal(learning_unit_yr, faculty_no_faculty_no_central, False))

    def test_can_modify_end_year_by_proposal_previous_n_year(self):
        faculty_person = FacultyManagerFactory()
        lcy = LearningContainerYearFactory(academic_year=self.previous_academic_year,
                                           container_type=learning_container_year_types.COURSE)
        learning_unit_yr = LearningUnitYearFactory(
            academic_year=self.previous_academic_year,
            subtype=learning_unit_year_subtypes.FULL,
            learning_unit=LearningUnitFactory(),
            learning_container_year=lcy
        )

        self._end_year_permission_assert(faculty_person, learning_unit_yr)
        central_person = CentralManagerFactory()
        self.assertFalse(can_modify_end_year_by_proposal(learning_unit_yr, central_person, False))

    def test_can_modify_end_year_by_proposal_n_year(self):
        faculty_person = FacultyManagerFactory()
        lcy = LearningContainerYearFactory(academic_year=self.current_academic_year,
                                           container_type=learning_container_year_types.COURSE)
        learning_unit_yr = LearningUnitYearFactory(
            academic_year=self.current_academic_year,
            subtype=learning_unit_year_subtypes.FULL,
            learning_unit=LearningUnitFactory(),
            learning_container_year=lcy
        )

        self._end_year_permission_assert(faculty_person, learning_unit_yr)
        central_person = CentralManagerFactory()
        self.assertTrue(can_modify_end_year_by_proposal(learning_unit_yr, central_person, True))

    def test_can_modify_end_year_by_proposal_n_year_plus_one(self):
        faculty_person = FacultyManagerFactory()
        lcy = LearningContainerYearFactory(academic_year=self.next_academic_yr,
                                           container_type=learning_container_year_types.COURSE)
        learning_unit_yr = LearningUnitYearFactory(
            academic_year=self.next_academic_yr,
            subtype=learning_unit_year_subtypes.FULL,
            learning_unit=LearningUnitFactory(),
            learning_container_year=lcy
        )

        self.assertTrue(can_modify_end_year_by_proposal(learning_unit_yr, faculty_person, True))
        central_person = CentralManagerFactory()
        self.assertTrue(can_modify_end_year_by_proposal(learning_unit_yr, central_person, True))

    def test_can_modify_by_proposal_previous_n_year(self):
        faculty_person = FacultyManagerFactory()
        lcy = LearningContainerYearFactory(academic_year=self.previous_academic_year,
                                           container_type=learning_container_year_types.COURSE)
        learning_unit_yr = LearningUnitYearFactory(
            academic_year=self.previous_academic_year,
            subtype=learning_unit_year_subtypes.FULL,
            learning_unit=LearningUnitFactory(),
            learning_container_year=lcy
        )

        self._modify_permission_assert(faculty_person, learning_unit_yr)
        central_person = CentralManagerFactory()
        self.assertFalse(can_modify_by_proposal(learning_unit_yr, central_person, False))

    def test_can_modify_by_proposal_n_year(self):
        faculty_person = FacultyManagerFactory()
        lcy = LearningContainerYearFactory(academic_year=self.current_academic_year,
                                           container_type=learning_container_year_types.COURSE)
        learning_unit_yr = LearningUnitYearFactory(
            academic_year=self.current_academic_year,
            subtype=learning_unit_year_subtypes.FULL,
            learning_unit=LearningUnitFactory(),
            learning_container_year=lcy
        )

        self._modify_permission_assert(faculty_person, learning_unit_yr)
        central_person = CentralManagerFactory()
        self.assertTrue(can_modify_by_proposal(learning_unit_yr, central_person, True))

    def test_can_modify_by_proposal_n_year_plus_one(self):
        faculty_person = FacultyManagerFactory()
        lcy = LearningContainerYearFactory(academic_year=self.next_academic_yr,
                                           container_type=learning_container_year_types.COURSE)
        learning_unit_yr = LearningUnitYearFactory(
            academic_year=self.next_academic_yr,
            subtype=learning_unit_year_subtypes.FULL,
            learning_unit=LearningUnitFactory(),
            learning_container_year=lcy
        )

        self.assertTrue(can_modify_by_proposal(learning_unit_yr, faculty_person, True))
        central_person = CentralManagerFactory()
        self.assertTrue(can_modify_by_proposal(learning_unit_yr, central_person, True))

    def _build_user_with_permission_to_consolidate(self):
        a_person = PersonFactory()
        a_person.user.user_permissions.add(Permission.objects.get(codename="can_consolidate_learningunit_proposal"))
        return a_person.user

    def _get_result_data_expected_for_proposal(self, id_li, title, class_li):
        if class_li != "":
            url = "#"
        else:
            url = self.url_edit
        return {
            'load_modal': False,
            'id_li': id_li,
            'url': url,
            'title': title,
            'class_li': class_li,
            'text': "",
            'js_script': ""

        }

    def _get_result_data_expected(self, id_li, title='', url="#"):

        return {
            'load_modal': False,
            'id_li': id_li,
            'url': url,
            'title': title,
            'class_li': self._get_class(title),
            'text': '',
            'data_target': '',
        }

    def _get_result_data_expected_delete(self, id_li, title='', load_modal=False, data_target='', url="#"):

        return {
            'load_modal': load_modal,
            'id_li': id_li,
            'url': url,
            'title': title,
            'class_li': self._get_class(title),
            'text': '',
            'data_target': data_target,
        }

    def _get_class(self, title):
        return DISABLED if title != '' else ''

    def _get_result_data_expected_for_proposal_suppression(self, id_li, title, class_li):
        if class_li != "":
            url = "#"
        else:
            url = self.url_edit
        return {
            'load_modal': False,
            'id_li': id_li,
            'url': url,
            'title': title,
            'class_li': class_li,
            'text': "",
            'data_target': "",

        }

    def _end_year_permission_assert(self, a_person, luy):
        self.assertFalse(can_modify_end_year_by_proposal(luy, a_person, False))
        with self.assertRaises(PermissionDenied) as perm_ex:
            can_modify_end_year_by_proposal(luy, a_person, True)
        self.assertEqual('{}'.format(perm_ex.exception), MSG_NOT_ELIGIBLE_TO_MODIFY_END_YEAR_PROPOSAL_ON_THIS_YEAR)

    def _modify_permission_assert(self, a_person, luy):
        self.assertFalse(can_modify_by_proposal(luy, a_person, False))
        with self.assertRaises(PermissionDenied) as perm_ex:
            can_modify_by_proposal(luy, a_person, True)
        self.assertEqual('{}'.format(perm_ex.exception), MSG_NOT_ELIGIBLE_TO_PUT_IN_PROPOSAL_ON_THIS_YEAR)
