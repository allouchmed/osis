##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2017 Université catholique de Louvain (http://www.uclouvain.be)
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

from base.forms.learning_unit.external_learning_unit import ExternalLearningUnitBaseForm, \
    LearningContainerYearExternalModelForm, CograduationExternalLearningUnitModelForm, \
    LearningUnitYearForExternalModelForm
from base.forms.learning_unit.learning_unit_create import LearningUnitYearModelForm, \
    LearningUnitModelForm
from base.forms.learning_unit.search_form import ExternalLearningUnitYearForm
from base.models.enums import learning_unit_year_subtypes
from base.models.enums import organization_type
from base.models.enums.learning_container_year_types import EXTERNAL
from base.models.enums.learning_unit_year_subtypes import FULL
from base.models.learning_unit_year import LearningUnitYear
from base.tests.factories.academic_year import create_current_academic_year
from base.tests.factories.business.entities import create_entities_hierarchy
from base.tests.factories.campus import CampusFactory
from base.tests.factories.external_learning_unit_year import ExternalLearningUnitYearFactory
from base.tests.factories.learning_container_year import LearningContainerYearFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory, LearningUnitYearFullFactory
from base.tests.factories.organization import OrganizationFactory
from base.tests.factories.organization_address import OrganizationAddressFactory
from base.tests.factories.person import PersonFactory
from base.tests.factories.person_entity import PersonEntityFactory
from reference.tests.factories.language import LanguageFactory

NAMEN = 'Namur'


def get_valid_external_learning_unit_form_data(academic_year, person, learning_unit_year=None):
    entities = create_entities_hierarchy()
    PersonEntityFactory(person=person, entity=entities['root_entity'], with_child=True)
    requesting_entity = entities['child_one_entity_version']
    organization = OrganizationFactory(type=organization_type.MAIN)
    campus = CampusFactory(organization=organization)
    language = LanguageFactory(code='FR')

    if not learning_unit_year:
        container_year = LearningContainerYearFactory(academic_year=academic_year)
        learning_unit_year = LearningUnitYearFactory.build(
            acronym='EOSIS1111',
            academic_year=academic_year,
            learning_container_year=container_year,
            subtype=learning_unit_year_subtypes.FULL,
            campus=campus,
            language=language
        )
    return {
        # Learning unit year data model form
        'acronym_0': learning_unit_year.acronym[0],
        'acronym_1': learning_unit_year.acronym[1:],
        'academic_year': learning_unit_year.academic_year.id,
        'specific_title': learning_unit_year.specific_title,
        'specific_title_english': learning_unit_year.specific_title_english,
        'credits': learning_unit_year.credits,
        'status': learning_unit_year.status,
        'campus': learning_unit_year.campus.id,
        'language': learning_unit_year.language.pk,
        'periodicity': learning_unit_year.periodicity,

        # Learning unit data model form
        'faculty_remark': learning_unit_year.learning_unit.faculty_remark,

        # Learning container year data model form
        'common_title': learning_unit_year.learning_container_year.common_title,
        'common_title_english': learning_unit_year.learning_container_year.common_title_english,
        'is_vacant': learning_unit_year.learning_container_year.is_vacant,

        # External learning unit model form
        'requirement_entity-entity': requesting_entity.id,
        'allocation_entity-entity': requesting_entity.id,
        'external_acronym': 'Gorzyne',
        'external_credits': '5',

        # Learning component year data model form
        'component-TOTAL_FORMS': '2',
        'component-INITIAL_FORMS': '0',
        'component-MAX_NUM_FORMS': '2',
        'component-0-hourly_volume_total_annual': 20,
        'component-0-hourly_volume_partial_q1': 10,
        'component-0-hourly_volume_partial_q2': 10,
        'component-1-hourly_volume_total_annual': 20,
        'component-1-hourly_volume_partial_q1': 10,
        'component-1-hourly_volume_partial_q2': 10,
    }


class TestExternalLearningUnitForm(TestCase):
    def setUp(self):
        self.person = PersonFactory()
        self.academic_year = create_current_academic_year()
        self.language = LanguageFactory(code='FR')

    def test_external_learning_unit_form_init(self):
        form = ExternalLearningUnitBaseForm(person=self.person, academic_year=self.academic_year)

        context = form.get_context()
        self.assertEqual(context['subtype'], FULL)
        self.assertIsInstance(context['learning_unit_form'], LearningUnitModelForm)
        self.assertIsInstance(context['learning_unit_year_form'], LearningUnitYearModelForm)
        self.assertIsInstance(context['learning_container_year_form'], LearningContainerYearExternalModelForm)
        self.assertIsInstance(context['learning_unit_external_form'], CograduationExternalLearningUnitModelForm)

    def test_external_learning_unit_form_is_valid(self):
        data = get_valid_external_learning_unit_form_data(self.academic_year, self.person)
        form = ExternalLearningUnitBaseForm(person=self.person, academic_year=self.academic_year, data=data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_external_learning_unit_form_save(self):
        data = get_valid_external_learning_unit_form_data(self.academic_year, self.person)
        form = ExternalLearningUnitBaseForm(person=self.person, academic_year=self.academic_year, data=data,
                                            start_year=self.academic_year.year)
        self.assertTrue(form.is_valid(), form.errors)
        luy = form.save()

        self.assertIsInstance(luy, LearningUnitYear)
        self.assertEqual(luy.learning_container_year.container_type, EXTERNAL)
        self.assertEqual(luy.acronym[0], 'E')
        self.assertEqual(luy.externallearningunityear.author, self.person)
        self.assertEqual(luy.learning_unit.start_year, self.academic_year.year)


class TestLearningUnitYearForExternalModelForm(TestCase):
    def setUp(self):
        self.person = PersonFactory()
        self.academic_year = create_current_academic_year()
        self.language = LanguageFactory(code='FR')

    def test_init(self):
        campus = CampusFactory()
        address = OrganizationAddressFactory(is_main=True, organization=campus.organization)

        luy = LearningUnitYearFullFactory(campus=campus)

        form = LearningUnitYearForExternalModelForm(
            person=self.person, data=None,
            subtype=FULL, instance=luy, initial={})
        self.assertEqual(form.initial["country_external_institution"], address.country.pk)


class TestExternalLearningUnitSearchForm(TestCase):
    def setUp(self):
        self.academic_year = create_current_academic_year()

        self.be_organization_adr_city1 = OrganizationAddressFactory(country__iso_code="BE", city=NAMEN)
        self.external_lu_1 = ExternalLearningUnitYearFactory(
            co_graduation=True,
            learning_unit_year__academic_year=self.academic_year,
            learning_unit_year__acronym='EDROI1001',
            learning_unit_year__campus__organization=self.be_organization_adr_city1.organization,
        )

        self.be_organization_adr_city2 = OrganizationAddressFactory(country__iso_code="BE", city='Bruxelles')
        self.external_lu_2 = ExternalLearningUnitYearFactory(
            co_graduation=True,
            learning_unit_year__academic_year=self.academic_year,
            learning_unit_year__acronym='EDROI1002',
            learning_unit_year__campus__organization=self.be_organization_adr_city2.organization,
        )

    def test_search_learning_units_on_acronym(self):
        form_data = {
            "acronym": self.external_lu_1.learning_unit_year.acronym,
        }

        form = ExternalLearningUnitYearForm(form_data)
        self.assertTrue(form.is_valid())
        self.assertCountEqual(form.get_activity_learning_units(), [self.external_lu_1.learning_unit_year])

    def test_search_learning_units_on_partial_acronym(self):
        form_data = {
            "acronym": self.external_lu_1.learning_unit_year.acronym[:5],
        }

        form = ExternalLearningUnitYearForm(form_data)
        self.assertTrue(form.is_valid())
        self.assertCountEqual(form.get_activity_learning_units(), [
            self.external_lu_1.learning_unit_year,
            self.external_lu_2.learning_unit_year
        ])

    def test_search_learning_units_by_country(self):
        form_data = {
            "country": self.external_lu_1.learning_unit_year.campus.organization.country.id,
        }

        form = ExternalLearningUnitYearForm(form_data)
        self.assertTrue(form.is_valid())
        self.assertCountEqual(form.get_activity_learning_units(), [
            self.external_lu_1.learning_unit_year, self.external_lu_2.learning_unit_year])

    def test_search_learning_units_by_city(self):
        form_data = {
            "city": NAMEN,
        }

        form = ExternalLearningUnitYearForm(form_data)
        self.assertTrue(form.is_valid())
        self.assertCountEqual(form.get_activity_learning_units(), [self.external_lu_1.learning_unit_year])

    def test_search_learning_units_by_campus(self):
        form_data = {

            "campus": self.external_lu_1.learning_unit_year.campus.id,
        }

        form = ExternalLearningUnitYearForm(form_data)
        self.assertTrue(form.is_valid())
        self.assertCountEqual(form.get_activity_learning_units(), [self.external_lu_1.learning_unit_year])

    def test_assert_ignore_external_learning_units_of_type_mobility(self):
        original_count = LearningUnitYear.objects.filter(externallearningunityear__co_graduation=True, externallearningunityear__mobility=False).count()
        ExternalLearningUnitYearFactory(
            learning_unit_year__academic_year=self.academic_year,
            mobility=True,
            co_graduation=False,
            learning_unit_year__acronym="XTEST1234",
        )
        form_data = {
            "academic_year": self.academic_year.id,
        }
        form = ExternalLearningUnitYearForm(form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.get_activity_learning_units().count(), original_count)
