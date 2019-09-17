##############################################################################
#
# OSIS stands for Open Student Information System. It's an application
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
import datetime

import factory
import factory.fuzzy
from django.test import TestCase
from django.utils import timezone

from base.business.learning_units.perms import find_last_requirement_entity_version
from base.models import entity_version
from base.models.entity_version import build_current_entity_version_structure_in_memory, \
    find_parent_of_type_into_entity_structure, get_structure_of_entity_version, \
    get_entity_version_parent_or_itself_from_type
from base.models.enums import organization_type
from base.models.enums.entity_type import FACULTY, SCHOOL
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.entity import EntityFactory
from base.tests.factories.entity_version import EntityVersionFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.organization import OrganizationFactory
from base.tests.factories.person import PersonFactory
from base.tests.factories.person_entity import PersonEntityFactory
from osis_common.utils.datetime import get_tzinfo
from reference.tests.factories.country import CountryFactory

now = datetime.datetime.now()


class EntityVersionTest(TestCase):
    def setUp(self):
        self.country = CountryFactory()
        self.organization = OrganizationFactory(type=organization_type.MAIN)
        self.entities = [EntityFactory(country=self.country, organization=self.organization) for x in range(3)]
        self.parent = EntityFactory(country=self.country, organization=self.organization)
        self.start_date = datetime.date(2015, 1, 1)
        self.end_date = datetime.date(2015, 12, 31)
        self.date_in_2015 = factory.fuzzy.FuzzyDate(datetime.date(2015, 1, 1),
                                                    datetime.date(2015, 12, 30)).fuzz()
        self.date_in_2017 = factory.fuzzy.FuzzyDate(datetime.date(2017, 1, 1),
                                                    datetime.date(2017, 12, 30)).fuzz()

        self.entity_versions = [EntityVersionFactory(
            entity=self.entities[x],
            acronym="ENTITY_V_" + str(x),
            title="This is the entity version " + str(x),
            entity_type="FACULTY",
            parent=self.parent,
            start_date=self.start_date,
            end_date=self.end_date
        )
            for x in range(3)]
        self.parent_entity_version = EntityVersionFactory(entity=self.parent,
                                                          acronym="ENTITY_PARENT",
                                                          title="This is the entity parent version",
                                                          entity_type="SECTOR",
                                                          start_date=self.start_date,
                                                          end_date=self.end_date)

    def test_create_entity_version_same_entity_same_dates(self):
        with self.assertRaisesMessage(AttributeError, 'EntityVersion invalid parameters'):
            EntityVersionFactory(
                entity=self.entities[0],
                start_date=self.start_date,
                end_date=self.end_date
            )

    def test_create_entity_version_same_entity_overlapping_dates_end_date_in(self):
        with self.assertRaisesMessage(AttributeError, 'EntityVersion invalid parameters'):
            EntityVersionFactory(
                entity=self.entities[0],
                start_date=factory.fuzzy.FuzzyDate(datetime.date(2010, 1, 1),
                                                   datetime.date(2014, 12, 30)).fuzz(),
                end_date=factory.fuzzy.FuzzyDate(datetime.date(2015, 1, 1),
                                                 datetime.date(2015, 12, 30)).fuzz()
            )

    def test_create_entity_version_same_entity_overlapping_dates_start_date_in(self):
        with self.assertRaisesMessage(AttributeError, 'EntityVersion invalid parameters'):
            EntityVersionFactory(
                entity=self.entities[0],
                start_date=factory.fuzzy.FuzzyDate(datetime.date(2015, 1, 1),
                                                   datetime.date(2015, 12, 30)).fuzz(),
                end_date=factory.fuzzy.FuzzyDate(datetime.date(2016, 1, 1),
                                                 datetime.date(2020, 12, 30)).fuzz()
            )

    def test_create_entity_version_same_entity_overlapping_dates_both_dates_out(self):
        with self.assertRaisesMessage(AttributeError, 'EntityVersion invalid parameters'):
            EntityVersionFactory(
                entity=self.entities[0],
                start_date=factory.fuzzy.FuzzyDate(datetime.date(2010, 1, 1),
                                                   datetime.date(2014, 12, 30)).fuzz(),
                end_date=factory.fuzzy.FuzzyDate(datetime.date(2016, 1, 1),
                                                 datetime.date(2020, 12, 30)).fuzz()
            )

    def test_create_entity_version_same_entity_overlapping_dates_both_dates_in(self):
        with self.assertRaisesMessage(AttributeError, 'EntityVersion invalid parameters'):
            EntityVersionFactory(
                entity=self.entities[0],
                start_date=factory.fuzzy.FuzzyDate(datetime.date(2015, 1, 1),
                                                   datetime.date(2015, 6, 30)).fuzz(),
                end_date=factory.fuzzy.FuzzyDate(datetime.date(2015, 7, 1),
                                                 datetime.date(2015, 12, 30)).fuzz()
            )

    def test_create_entity_version_same_acronym_overlapping_dates_end_date_in(self):
        with self.assertRaisesMessage(AttributeError, 'EntityVersion invalid parameters'):
            EntityVersionFactory(
                acronym=self.entity_versions[0].acronym,
                start_date=factory.fuzzy.FuzzyDate(datetime.date(2010, 1, 1),
                                                   datetime.date(2014, 12, 30)).fuzz(),
                end_date=factory.fuzzy.FuzzyDate(datetime.date(2015, 1, 1),
                                                 datetime.date(2015, 12, 30)).fuzz()
            )

    def test_create_entity_version_same_acronym_overlapping_dates_start_date_in(self):
        with self.assertRaisesMessage(AttributeError, 'EntityVersion invalid parameters'):
            EntityVersionFactory(
                acronym=self.entity_versions[0].acronym,
                start_date=factory.fuzzy.FuzzyDate(datetime.date(2015, 1, 1),
                                                   datetime.date(2015, 12, 30)).fuzz(),
                end_date=factory.fuzzy.FuzzyDate(datetime.date(2016, 1, 1),
                                                 datetime.date(2020, 12, 30)).fuzz()
            )

    def test_create_entity_version_same_acronym_overlapping_dates_both_dates_out(self):
        with self.assertRaisesMessage(AttributeError, 'EntityVersion invalid parameters'):
            EntityVersionFactory(
                acronym=self.entity_versions[0].acronym,
                start_date=factory.fuzzy.FuzzyDate(datetime.date(2010, 1, 1),
                                                   datetime.date(2014, 12, 30)).fuzz(),
                end_date=factory.fuzzy.FuzzyDate(datetime.date(2016, 1, 1),
                                                 datetime.date(2020, 12, 30)).fuzz()
            )

    def test_create_entity_version_same_acronym_overlapping_dates_both_dates_in(self):
        with self.assertRaisesMessage(AttributeError, 'EntityVersion invalid parameters'):
            EntityVersionFactory(
                acronym=self.entity_versions[0].acronym,
                start_date=factory.fuzzy.FuzzyDate(datetime.date(2015, 1, 1),
                                                   datetime.date(2015, 6, 30)).fuzz(),
                end_date=factory.fuzzy.FuzzyDate(datetime.date(2015, 7, 1),
                                                 datetime.date(2015, 12, 30)).fuzz()
            )

    def test_find_entity_version(self):
        search_date = factory.fuzzy.FuzzyDate(datetime.date(2015, 1, 1),
                                              datetime.date(2015, 12, 30)).fuzz()
        self.assertEqual(entity_version.find("ENTITY_V_0", search_date), self.entity_versions[0])
        self.assertEqual(entity_version.find("ENTITY_V_1", search_date), self.entity_versions[1])
        self.assertEqual(entity_version.find("NOT_EXISTING_ENTITY", search_date), None)
        ev = entity_version.find_by_id(self.entity_versions[0].id)
        self.assertEqual(ev, self.entity_versions[0])
        self.assertEqual(str(ev), str(self.entity_versions[0]))
        self.assertIsNone(entity_version.find_by_id(None))

    def test_search_matching_entity_version(self):
        self.assertCountEqual(
            entity_version.search(
                entity=self.entities[0].id,
                acronym="ENTITY_V_0",
                title="This is the entity version 0",
                entity_type="FACULTY",
                start_date=self.start_date,
                end_date=self.end_date
            ),
            [self.entity_versions[0]]
        )

    def test_search_not_matching_entity_versions(self):
        self.assertCountEqual(
            entity_version.search(
                entity=self.entities[0].id,
                acronym="FNVABAB",
                title="There is no version matching this search",
                entity_type="FACULTY",
                start_date=self.start_date,
                end_date=self.end_date
            ),
            []
        )

        self.assertCountEqual(
            entity_version.search(
                entity=self.entities[0].id,
                acronym="ENTITY_V_0",
                title="This is the entity version 0",
                entity_type="FACULTY",
                start_date=factory.fuzzy.FuzzyDate(datetime.date(2010, 1, 1),
                                                   datetime.date(2014, 12, 30)).fuzz(),
                end_date=factory.fuzzy.FuzzyDate(datetime.date(2010, 1, 1),
                                                 datetime.date(2014, 12, 30)).fuzz(),
            ),
            []
        )

    def test_version_direct_children_in_dates(self):
        self.assertCountEqual(self.parent_entity_version.find_direct_children(date=self.date_in_2015),
                              [self.entity_versions[x] for x in range(3)])
        self.assertEqual(self.parent_entity_version.count_direct_children(date=self.date_in_2015), 3)

    def test_version_direct_children_out_dates(self):
        self.assertFalse(self.parent_entity_version.find_direct_children(date=self.date_in_2017).exists())
        self.assertEqual(self.parent_entity_version.count_direct_children(date=self.date_in_2017), 0)

    def test_version_direct_children_with_null_end(self):
        for version in self.entity_versions:
            version.end_date = None
            version.save()
            self.assertIsNone(version.end_date)
        self.parent_entity_version.end_date = None
        self.parent_entity_version.save()

        self.assertCountEqual(self.parent_entity_version.find_direct_children(date=self.date_in_2015),
                              [self.entity_versions[x] for x in range(3)])
        self.assertEqual(self.parent_entity_version.count_direct_children(date=self.date_in_2015), 3)

        self.assertCountEqual(self.parent_entity_version.find_direct_children(date=self.date_in_2017),
                              [self.entity_versions[x] for x in range(3)])
        self.assertEqual(self.parent_entity_version.count_direct_children(date=self.date_in_2017), 3)

    def test_version_get_parent(self):
        for child in self.entity_versions:
            self.assertEqual(child.get_parent_version(date=self.date_in_2015), self.parent_entity_version)
            self.assertEqual(child.get_parent_version(date=self.date_in_2017), None)

    def test_find_parent_of_type_itself(self):
        entity_v = EntityVersionFactory(entity_type=FACULTY)
        result = find_parent_of_type_into_entity_structure(
            entity_v,
            build_current_entity_version_structure_in_memory(timezone.now().date()),
            FACULTY
        )
        self.assertEqual(entity_v.entity, result)

    def test_find_parent_of_type_first_parent(self):
        entity = EntityFactory()
        EntityVersionFactory(entity=entity, entity_type=FACULTY)
        entity_v = EntityVersionFactory(parent=entity)
        result = find_parent_of_type_into_entity_structure(
            entity_v,
            build_current_entity_version_structure_in_memory(timezone.now().date()),
            FACULTY
        )
        self.assertEqual(entity_v.parent, result)

    def test_find_parent_of_type_without_parent(self):
        entity_v = EntityVersionFactory(parent=None, entity_type=SCHOOL)
        result = find_parent_of_type_into_entity_structure(
            entity_v,
            build_current_entity_version_structure_in_memory(timezone.now().date()),
            FACULTY
        )
        self.assertEqual(None, result)

    def test_find_parent_faculty_version(self):
        ac_yr = AcademicYearFactory()
        start_date = ac_yr.start_date
        end_date = ac_yr.end_date
        entity_faculty = EntityFactory(country=self.country, organization=self.organization)
        entity_faculty_version = EntityVersionFactory(
            entity=entity_faculty,
            acronym="ENTITY_FACULTY",
            title="This is the entity faculty ",
            entity_type="FACULTY",
            parent=None,
            start_date=start_date,
            end_date=end_date
        )
        entity_school_child_level1 = EntityFactory(country=self.country, organization=self.organization)
        EntityVersionFactory(entity=entity_school_child_level1,
                             acronym="ENTITY_LEVEL1",
                             title="This is the entity version level1 ",
                             entity_type="SCHOOL",
                             parent=entity_faculty,
                             start_date=start_date,
                             end_date=end_date)
        entity_school_child_level2 = EntityFactory(country=self.country, organization=self.organization)
        entity_school_version_level2 = EntityVersionFactory(
            entity=entity_school_child_level2,
            acronym="ENTITY_LEVEL2",
            title="This is the entity version level 2",
            entity_type="SCHOOL",
            parent=entity_school_child_level1,
            start_date=start_date,
            end_date=end_date
        )

        self.assertEqual(entity_school_version_level2.find_faculty_version(ac_yr),
                         entity_faculty_version)

    def test_find_parent_faculty_version_no_parent(self):
        start_date = datetime.datetime(now.year - 1, now.month, 16)
        end_date = datetime.datetime(now.year, now.month, 27)

        ac_yr = AcademicYearFactory(year=(now.year - 1),
                                    start_date=datetime.datetime(now.year - 1, now.month, 15),
                                    end_date=datetime.datetime(now.year, now.month, 28))
        entity_school_no_parent = EntityFactory(country=self.country, organization=self.organization)
        entity_school_version_no_parent = EntityVersionFactory(
            entity=entity_school_no_parent,
            acronym="ENTITY_LEVEL2",
            title="This is the entity version level 2",
            entity_type="SCHOOL",
            parent=None,
            start_date=start_date,
            end_date=end_date
        )

        self.assertIsNone(entity_school_version_no_parent.find_faculty_version(ac_yr))

    def test_find_parent_faculty_version_no_faculty_parent(self):

        start_date = datetime.datetime(now.year - 1, now.month, 16)
        end_date = datetime.datetime(now.year, now.month, 27)

        ac_yr = AcademicYearFactory(year=(now.year - 1),
                                    start_date=datetime.datetime(now.year - 1, now.month, 15),
                                    end_date=datetime.datetime(now.year, now.month, 28))

        entity_parent = EntityFactory(country=self.country, organization=self.organization)
        EntityVersionFactory(entity=entity_parent,
                             acronym="ENTITY_NOT_FACULTY",
                             title="This is not an entity faculty ",
                             entity_type="SCHOOL",
                             parent=None,
                             start_date=start_date,
                             end_date=end_date)
        entity_school_child_level1 = EntityFactory(country=self.country, organization=self.organization)
        entity_school_version_level1 = EntityVersionFactory(
            entity=entity_school_child_level1,
            acronym="ENTITY_LEVEL1",
            title="This is the entity version level1 ",
            entity_type="SCHOOL",
            parent=entity_parent,
            start_date=start_date,
            end_date=end_date
        )
        self.assertIsNone(entity_school_version_level1.find_faculty_version(ac_yr))

    def test_find_main_entities_version_filtered_by_person(self):
        person = PersonFactory()
        entity_attached = EntityFactory(organization=self.organization)
        entity_version_attached = EntityVersionFactory(entity=entity_attached, entity_type="SECTOR", parent=None,
                                                       end_date=None,
                                                       start_date=datetime.date.today() - datetime.timedelta(days=5))
        entity_not_attached = EntityFactory(organization=self.organization)
        EntityVersionFactory(entity=entity_not_attached, entity_type="SECTOR", parent=None, end_date=None)
        PersonEntityFactory(person=person, entity=entity_attached)
        entity_list = list(person.find_main_entities_version)
        self.assertTrue(entity_list)
        self.assertEqual(len(entity_list), 1)
        self.assertEqual(entity_list[0], entity_version_attached)

    def test_find_attached_faculty_entities_version_filtered_by_person(self):
        person = PersonFactory()
        entity_attached = EntityFactory(organization=self.organization)
        entity_version_attached = EntityVersionFactory(entity=entity_attached, entity_type="FACULTY")
        
        entity_not_attached = EntityFactory(organization=self.organization)
        EntityVersionFactory(entity=entity_not_attached, entity_type="SECTOR")
        
        entity_ilv = EntityFactory(organization=self.organization)
        entity_version_ilv = EntityVersionFactory(entity=entity_ilv, acronym="ILV")
        
        entity_parent = EntityFactory(organization=self.organization)
        entity_version_parent = EntityVersionFactory(entity=entity_parent, entity_type='FACULTY')
        EntityVersionFactory(parent=entity_parent)

        PersonEntityFactory(person=person, entity=entity_attached)
        PersonEntityFactory(person=person, entity=entity_ilv)
        PersonEntityFactory(person=person, entity=entity_parent)

        entity_list = list(person.find_attached_faculty_entities_version(acronym_exceptions=['ILV']))
        self.assertTrue(entity_list)
        self.assertEqual(len(entity_list), 3)
        self.assertIn(entity_version_attached, entity_list)
        self.assertIn(entity_version_ilv, entity_list)
        self.assertIn(entity_version_parent, entity_list)

    def test_find_attached_faculty_entities_version_filtered_by_person_but_faculty_below_attached_entities(self):
        person = PersonFactory()

        entity_attached = EntityFactory(organization=self.organization)
        EntityVersionFactory(entity=entity_attached, entity_type="SECTOR")

        entity_fac = EntityFactory(organization=self.organization)
        entity_version_fac = EntityVersionFactory(
            entity=entity_fac,
            acronym="FAC",
            entity_type="FACULTY",
            parent=entity_attached
        )

        PersonEntityFactory(person=person, entity=entity_attached)

        entity_list = list(person.find_attached_faculty_entities_version())
        self.assertTrue(entity_list)
        self.assertEqual(len(entity_list), 1)
        self.assertIn(entity_version_fac, entity_list)


class EntityVersionLoadInMemoryTest(TestCase):
    def setUp(self):
        self.country = CountryFactory()
        self.organization = OrganizationFactory(
            type=organization_type.MAIN
        )
        self.now = datetime.datetime.now(get_tzinfo())
        start_date = self.now - datetime.timedelta(days=10)
        end_date = None
        self._build_current_entity_version_structure(end_date, start_date)

    def _build_current_entity_version_structure(self, end_date, start_date):
        """Build the following entity version structure :
                             SST
                        SC        LOCI
                    MATH PHYS  URBA  BARC
        """
        self.root = EntityVersionFactory(
            entity=EntityFactory(country=self.country, organization=self.organization),
            acronym="SST",
            title="SST",
            entity_type=entity_version.entity_type.SECTOR,
            parent=None,
            start_date=start_date,
            end_date=end_date
        )
        self.SC = EntityVersionFactory(
            entity=EntityFactory(country=self.country, organization=self.organization),
            acronym="SC",
            title="SC",
            entity_type=entity_version.entity_type.FACULTY,
            parent=self.root.entity,
            start_date=start_date,
            end_date=end_date
        )
        self.MATH = EntityVersionFactory(
            entity=EntityFactory(country=self.country, organization=self.organization),
            acronym="MATH",
            title="MATH",
            entity_type=entity_version.entity_type.SCHOOL,
            parent=self.SC.entity,
            start_date=start_date,
            end_date=end_date
        )
        self.PHYS = EntityVersionFactory(
            entity=EntityFactory(country=self.country, organization=self.organization),
            acronym="PHYS",
            title="PHYS",
            entity_type=entity_version.entity_type.SCHOOL,
            parent=self.SC.entity,
            start_date=start_date,
            end_date=end_date
        )
        self.LOCI = EntityVersionFactory(
            entity=EntityFactory(country=self.country, organization=self.organization),
            acronym="LOCI",
            title="LOCI",
            entity_type=entity_version.entity_type.FACULTY,
            parent=self.root.entity,
            start_date=start_date,
            end_date=end_date
        )
        self.URBA = EntityVersionFactory(
            entity=EntityFactory(country=self.country, organization=self.organization),
            acronym="URBA",
            title="URBA",
            entity_type=entity_version.entity_type.SCHOOL,
            parent=self.LOCI.entity,
            start_date=start_date,
            end_date=end_date
        )
        self.BARC = EntityVersionFactory(
            entity=EntityFactory(country=self.country, organization=self.organization),
            acronym="BARC",
            title="BARC",
            entity_type=entity_version.entity_type.SCHOOL,
            parent=self.LOCI.entity,
            start_date=start_date,
            end_date=end_date
        )

    def test_build_entity_version_by_entity_id_parent(self):
        all_current_entities_version = entity_version.find_all_current_entities_version()
        result = entity_version._build_entity_version_by_entity_id(all_current_entities_version)
        expected_keys = [v.entity_id for v in all_current_entities_version]
        self.assertListEqual(list(sorted(result.keys())), sorted(expected_keys))

    def test_build_direct_children_by_entity_version_id(self):
        entity_version_by_entity_id = entity_version._build_entity_version_by_entity_id(
            entity_version.find_all_current_entities_version())
        result = entity_version._build_direct_children_by_entity_version_id(entity_version_by_entity_id)

        count_entities_version_with_children = 4
        self.assertEqual(len(result.keys()), count_entities_version_with_children)

        root_direct_children = [self.SC, self.LOCI]
        self.assertEqual(set(result[self.root.id]), set(root_direct_children))

        sc_direct_children = [self.MATH, self.PHYS]
        self.assertEqual(set(result[self.SC.id]), set(sc_direct_children))

        self.assertNotIn(self.MATH.id, result)  # No children for MATH

    def test_build_all_children_by_entity_version_id(self):
        all_current_entites_versions = entity_version.find_all_current_entities_version()
        entity_version_by_entity_id = entity_version._build_entity_version_by_entity_id(all_current_entites_versions)
        direct_children_by_entity_version_id = entity_version\
            ._build_direct_children_by_entity_version_id(entity_version_by_entity_id)
        result = entity_version._build_all_children_by_entity_version_id(direct_children_by_entity_version_id)

        count_entities_version_with_children = 4
        self.assertEqual(len(result.keys()), count_entities_version_with_children)

        root_all_children = [self.SC, self.LOCI, self.MATH, self.PHYS, self.URBA, self.BARC]
        self.assertEqual(set(result[self.root.id]), set(root_all_children))

        sc_all_children = [self.MATH, self.PHYS]
        self.assertEqual(set(result[self.SC.id]), set(sc_all_children))

        self.assertNotIn(self.MATH.id, result.keys())

    def test_build_entity_version_structure_in_memory(self):
        partial_expected_result = {
            self.root.entity.id: {
                'entity_version_parent': None,
                'direct_children': [self.SC, self.LOCI],
                'all_children': [self.SC, self.LOCI, self.MATH, self.PHYS, self.URBA, self.BARC],
            },
            self.SC.entity.id: {
                'entity_version_parent': self.root,
                'direct_children': [self.MATH, self.PHYS],
                'all_children': [self.MATH, self.PHYS],
            },
            self.MATH.entity.id: {
                'entity_version_parent': self.SC,
                'direct_children': [],
                'all_children': [],
            },
            # ...
        }
        result = entity_version.build_current_entity_version_structure_in_memory()
        all_current_entities_version = entity_version.find_all_current_entities_version()

        # assert entities without children are present in the result
        self.assertEqual(len(result.keys()), len(all_current_entities_version))
        self.assertEqual(result[self.MATH.entity.id]['all_children'], [])

    def test_get_structure_of_entity_version(self):
        result = entity_version.build_current_entity_version_structure_in_memory()
        self.assertEqual(
            get_structure_of_entity_version(entity_version.build_current_entity_version_structure_in_memory()),
            result)

        expected_result = None
        for r in result:
            if result[r]['entity_version'].acronym == self.root.acronym.upper():
                expected_result = result[r]
        self.assertEqual(
            get_structure_of_entity_version(entity_version.build_current_entity_version_structure_in_memory(),
                                            self.root.acronym),
            expected_result)

    def test_get_entity_version_from_type(self):
        structure = entity_version.build_current_entity_version_structure_in_memory()
        test_cases = [
            {"entity_version_test": self.MATH, 'entity_type': 'SECTOR', 'expected_result': self.root,
             'comment': 'to_test_sector'},
            {"entity_version_test": self.MATH, 'entity_type': 'FACULTY', 'expected_result': self.SC,
             'comment': 'to_test_faculty'},
            {"entity_version_test": self.MATH, 'entity_type': 'SCHOOL', 'expected_result': self.MATH,
             'comment': 'to_test_itself'},
            {"entity_version_test": self.root, 'entity_type': 'SCHOOL', 'expected_result': None,
             'comment': 'to_test_lt_itself'},
            {"entity_version_test": self.root, 'entity_type': 'SECTOR', 'expected_result': self.root,
             'comment': 'to_test_itself_without_parent'},
        ]

        for case in test_cases:
            with self.subTest(status_code=case.get('comment')):
                to_test = get_entity_version_parent_or_itself_from_type(entity_versions=structure,
                                                                        entity=case.get('entity_version_test').entity
                                                                        .most_recent_acronym,
                                                                        entity_type=case.get('entity_type'))
                self.assertEqual(case.get('expected_result'), to_test)


class TestFindLastEntityVersionByLearningUnitYearId(TestCase):
    def test_when_entity_version(self):
        learning_unit_year = LearningUnitYearFactory()

        actual_entity_version = find_last_requirement_entity_version(
            learning_unit_year_id=learning_unit_year.id,
        )

        self.assertIsNone(actual_entity_version)

    def test_find_last_entity_version_by_learning_unit_year_id(self):
        an_entity_version = EntityVersionFactory()
        learning_unit_year = LearningUnitYearFactory(
            learning_container_year__requirement_entity=an_entity_version.entity
        )

        actual_entity_version = find_last_requirement_entity_version(
            learning_unit_year_id=learning_unit_year.id,
        )
        self.assertEqual(an_entity_version, actual_entity_version)
