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

from unittest import mock

from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.test import TestCase, RequestFactory

from assessments.views import pgm_manager_administration
from base.models.program_manager import ProgramManager
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.entity_manager import EntityManagerFactory
from base.tests.factories.entity_version import EntityVersionFactory
from base.tests.factories.group import ProgramManagerGroupFactory
from base.tests.factories.offer_year import OfferYearFactory
from base.tests.factories.person import PersonFactory
from base.tests.factories.program_manager import ProgramManagerFactory
from base.tests.factories.structure import StructureFactory
from base.tests.factories.user import SuperUserFactory


class PgmManagerAdministrationTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        ProgramManagerGroupFactory()

        cls.user = SuperUserFactory()
        cls.person = PersonFactory()

        cls.entity_version_parent1 = EntityVersionFactory()

        cls.entity_version_child1 = EntityVersionFactory(parent=cls.entity_version_parent1.entity)
        cls.entity_version_child11 = EntityVersionFactory(parent=cls.entity_version_child1.entity)

        cls.entity_version_child2 = EntityVersionFactory(parent=cls.entity_version_parent1.entity)
        cls.entity_version_child21 = EntityVersionFactory(parent=cls.entity_version_child2.entity)
        cls.entity_version_child22 = EntityVersionFactory(parent=cls.entity_version_child2.entity)
        EntityManagerFactory(person__user=cls.user, entity=cls.entity_version_parent1.entity)

        cls.academic_year_previous, cls.academic_year_current = AcademicYearFactory.produce_in_past(quantity=2)

    def setUp(self):
        self.client.force_login(self.user)

    def test_remove_pgm_manager(self):
        egy1 = EducationGroupYearFactory(academic_year=self.academic_year_current)
        egy2 = EducationGroupYearFactory(academic_year=self.academic_year_current)
        pgm1 = ProgramManagerFactory(
            person=self.person,
            offer_year=OfferYearFactory(academic_year=egy1.academic_year, acronym=egy1.acronym),
            education_group=egy1.education_group
        )
        pgm2 = ProgramManagerFactory(
            person=self.person,
            offer_year=OfferYearFactory(academic_year=egy2.academic_year, acronym=egy2.acronym),
            education_group=egy2.education_group
        )
        response = self.client.get(
            reverse('delete_manager', args=[pgm1.pk]) + "?education_group_year={},{}".format(
                egy1.pk,
                egy2.pk
            )
        )
        self.assertEqual(response.context['other_programs'].get(), pgm2)

        self.client.post(
            reverse('delete_manager', args=[pgm1.pk]) + "?education_group_year={},{}".format(egy1.pk, egy2.pk)
        )
        self.assertFalse(ProgramManager.objects.filter(pk=pgm1.pk).exists())
        self.assertTrue(ProgramManager.objects.filter(pk=pgm2.pk).exists())

    def test_remove_multiple_pgm_manager(self):
        egy1 = EducationGroupYearFactory(academic_year=self.academic_year_current)
        egy2 = EducationGroupYearFactory(academic_year=self.academic_year_current)
        pgm1 = ProgramManagerFactory(
            person=self.person,
            offer_year=OfferYearFactory(academic_year=egy1.academic_year, acronym=egy1.acronym),
            education_group=egy1.education_group
        )
        pgm2 = ProgramManagerFactory(
            person=self.person,
            offer_year=OfferYearFactory(academic_year=egy2.academic_year, acronym=egy2.acronym),
            education_group=egy2.education_group
        )

        response = self.client.get(
            reverse('delete_manager_person', args=[self.person.pk]) + "?education_group_year={},{}".format(
                egy1.pk,
                egy2.pk
            )
        )
        self.assertFalse(response.context['other_programs'])

        self.client.post(
            reverse('delete_manager_person', args=[self.person.pk]) + "?education_group_year={},{}".format(
                egy1.pk,
                egy2.pk
            )
        )
        self.assertFalse(ProgramManager.objects.filter(pk=pgm1.pk).exists())
        self.assertFalse(ProgramManager.objects.filter(pk=pgm2.pk).exists())

    def test_main_programmanager_update(self):
        egy1 = EducationGroupYearFactory(academic_year=self.academic_year_current)
        egy2 = EducationGroupYearFactory(academic_year=self.academic_year_current)
        pgm1 = ProgramManagerFactory(
            person=self.person,
            offer_year=OfferYearFactory(academic_year=egy1.academic_year, acronym=egy1.acronym),
            education_group=egy1.education_group
        )
        pgm2 = ProgramManagerFactory(
            person=self.person,
            offer_year=OfferYearFactory(academic_year=egy2.academic_year, acronym=egy2.acronym),
            education_group=egy2.education_group
        )

        self.client.post(
            reverse('update_main_person', args=[self.person.pk]) + "?education_group_year={},{}".format(
                egy1.pk,
                egy2.pk
            ), data={'is_main': 'true'}
        )
        pgm1.refresh_from_db()
        pgm2.refresh_from_db()
        self.assertTrue(pgm1.is_main)
        self.assertTrue(pgm2.is_main)

        self.client.post(
            reverse('update_main', args=[pgm1.pk]) + "?education_group_year={},{}".format(
                egy1.pk,
                egy2.pk
            ), data={'is_main': 'false'}
        )
        pgm1.refresh_from_db()
        pgm2.refresh_from_db()
        self.assertFalse(pgm1.is_main)
        self.assertTrue(pgm2.is_main)

    def test_list_pgm_manager(self):
        egy1 = EducationGroupYearFactory(academic_year=self.academic_year_current)
        egy2 = EducationGroupYearFactory(academic_year=self.academic_year_current)
        pgm1 = ProgramManagerFactory(
            person=self.person,
            offer_year=OfferYearFactory(academic_year=egy1.academic_year, acronym=egy1.acronym),
            education_group=egy1.education_group
        )
        pgm2 = ProgramManagerFactory(
            person=self.person,
            offer_year=OfferYearFactory(academic_year=egy2.academic_year, acronym=egy2.acronym),
            education_group=egy2.education_group
        )

        response = self.client.get(
            reverse('manager_list'), data={'education_group_year': [egy1.pk, egy2.pk]}
        )
        self.assertEqual(
            response.context['by_person'], {self.person: [pgm1, pgm2]}
        )

    def test_education_group_year_queried_by_academic_year(self):
        an_entity_management = EntityVersionFactory()
        EducationGroupYearFactory(academic_year=self.academic_year_previous, management_entity=an_entity_management.entity)
        EducationGroupYearFactory(academic_year=self.academic_year_current, management_entity=an_entity_management.entity)
        EducationGroupYearFactory(academic_year=self.academic_year_current, management_entity=an_entity_management.entity)

        self.assertEqual(len(pgm_manager_administration._get_programs(self.academic_year_current,
                                                                      [an_entity_management.entity],
                                                                      None,
                                                                      None)), 2)
        self.assertEqual(len(pgm_manager_administration._get_programs(self.academic_year_previous,
                                                                      [an_entity_management.entity],
                                                                      None,
                                                                      None)), 1)

    def test_pgm_manager_queried_by_academic_year(self):
        a_management_entity = EntityVersionFactory()
        egy_previous_year = EducationGroupYearFactory(
            academic_year=self.academic_year_previous,
            administration_entity=a_management_entity.entity
        )
        egy_current_year = EducationGroupYearFactory(
            academic_year=self.academic_year_current,
            administration_entity=a_management_entity.entity
        )
        person_previous_year = PersonFactory()
        person_current_year = PersonFactory()

        ProgramManagerFactory(person=person_previous_year, education_group=egy_previous_year.education_group)
        ProgramManagerFactory(person=person_current_year, education_group=egy_current_year.education_group)

        self.assertEqual(len(pgm_manager_administration._get_entity_program_managers([{'root': a_management_entity}],
                                                                                     self.academic_year_current)), 1)

    @mock.patch('django.contrib.auth.decorators')
    def test_get_entity_root_selected_all(self, mock_decorators):
        post_request = set_post_request(mock_decorators, {'entity': 'all_ESPO'}, '/pgm_manager/search')
        self.assertEqual(pgm_manager_administration.get_entity_root_selected(post_request), 'ESPO')

    @mock.patch('django.contrib.auth.decorators')
    def test_get_entity_root_selected(self, mock_decorators):
        post_request = set_post_request(mock_decorators, {'entity': '2',
                                                          'entity_root': '2'}, '/pgm_manager/search')
        self.assertEqual(pgm_manager_administration.get_entity_root_selected(post_request), '2')

    @mock.patch('django.contrib.auth.decorators')
    def test_get_filter_value(self, mock_decorators):
        request = set_post_request(mock_decorators, {'offer_type': '-'}, '/pgm_manager/search')
        self.assertIsNone(pgm_manager_administration.get_filter_value(request, 'offer_type'))
        request = set_post_request(mock_decorators, {'offer_type': '1'}, '/pgm_manager/search')
        self.assertEqual(pgm_manager_administration.get_filter_value(request, 'offer_type'), '1')

    def test_get_entity_list_for_one_entity(self):
        self.assertEqual(len(pgm_manager_administration.get_entity_list(self.entity_version_parent1.id, None)), 1)

    def test_add_program_managers(self):
        egy1 = EducationGroupYearFactory(academic_year=self.academic_year_current)
        OfferYearFactory(academic_year=self.academic_year_current,
                         acronym=egy1.acronym)
        egy2 = EducationGroupYearFactory(academic_year=self.academic_year_current)
        OfferYearFactory(academic_year=self.academic_year_current,
                         acronym=egy2.acronym)

        self.client.post(
            reverse("create_manager_person") + "?education_group_year={},{}".format(egy1.pk, egy2.pk),
            data={'person': self.person.pk}
        )
        self.assertEqual(ProgramManager.objects.filter(person=self.person).count(), 2)

    def test_get_administrator_entities_acronym_list(self):
        structure_root_1 = StructureFactory(acronym='A')

        structure_child_1 = StructureFactory(acronym='AA', part_of=structure_root_1)
        structure_child_2 = StructureFactory(acronym='BB', part_of=structure_root_1)

        structure_root_2 = StructureFactory(acronym='B')

        data = [{'root': structure_root_1, 'structures': [structure_root_1, structure_child_1, structure_child_2]},
                {'root': structure_root_2, 'structures': []}]

        EntityManagerFactory(person=self.person,
                             structure=structure_root_1)

        data = pgm_manager_administration._get_administrator_entities_acronym_list(data)

        self.assertEqual(data, "A, B")


def set_post_request(mock_decorators, data_dict, url):
    mock_decorators.login_required = lambda x: x
    request_factory = RequestFactory()
    request = request_factory.post(url, data_dict)
    request.user = mock.Mock()
    return request


class TestAddSaveProgramManager(TestCase):
    @classmethod
    def setUpTestData(cls):
        ProgramManagerGroupFactory()
        cls.person = PersonFactory()
        cls.offer_year_without_equivalent_education_group_year = OfferYearFactory(
            corresponding_education_group_year=None
        )

        acronym = "Acronym"
        cls.education_group_year = EducationGroupYearFactory(acronym=acronym)
        cls.offer_year = OfferYearFactory(
            acronym=acronym,
            corresponding_education_group_year=cls.education_group_year
        )

    def test_when_offer_year_has_no_equivalent_education_group_year(self):
        with self.assertRaises(IntegrityError):
            ProgramManager(
                offer_year=self.offer_year_without_equivalent_education_group_year,
                person=self.person
            ).save()

    def test_when_offer_year_has_an_equivalent_education_group_year(self):
        pgm_manager = ProgramManager(offer_year=self.offer_year, person=self.person)
        pgm_manager.save()
        self.assertTrue(pgm_manager.id)
        self.assertEqual(pgm_manager.person, self.person)
        self.assertEqual(pgm_manager.offer_year, self.offer_year)
        self.assertEqual(pgm_manager.education_group, self.education_group_year.education_group)
