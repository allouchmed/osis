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
from unittest import mock

from django.test import TestCase
from django.urls import reverse

from base.tests.factories.education_group_year import EducationGroupYearFactory, TrainingFactory, MiniTrainingFactory
from base.tests.factories.group_element_year import GroupElementYearFactory
from base.tests.factories.person import PersonFactory
from base.utils.cache import cache, ElementCache


class TestAttachTypeDialogView(TestCase):
    def setUp(self):
        self.root_egy = TrainingFactory()
        self.egy = MiniTrainingFactory(academic_year=self.root_egy.academic_year)
        self.group_element_year=  GroupElementYearFactory(
            parent__academic_year=self.root_egy.academic_year,
            child_branch=self.egy
        )
        self.selected_egy = EducationGroupYearFactory(
            academic_year=self.root_egy.academic_year
        )

        self.url = reverse(
            "education_group_attach",
            args=[self.root_egy.id, self.egy.id]
        )

        self.person = PersonFactory()

        self.client.force_login(self.person.user)
        self.perm_patcher = mock.patch("base.business.education_groups.perms.is_eligible_to_change_education_group",
                                       return_value=True)
        self.mocked_perm = self.perm_patcher.start()

        self.addCleanup(self.mocked_perm.stop)
        self.addCleanup(cache.clear)

    def test_context_data(self):
        ElementCache(self.person.user).save_element_selected(self.selected_egy,
                                                             source_link_id=self.group_element_year.id)
        response = self.client.get(self.url)
        context = response.context

        self.assertEqual(context["object_to_attach"], self.selected_egy)
        self.assertEqual(context["source_link"], self.group_element_year)
        self.assertEqual(context["education_group_year_parent"], self.egy)
