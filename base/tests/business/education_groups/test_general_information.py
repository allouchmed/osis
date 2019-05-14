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

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponseNotFound, HttpResponse
from django.test import TestCase, override_settings
from requests import Timeout

from base.business.education_groups import general_information
from base.business.education_groups.general_information import PublishException, _bulk_publish, \
    _get_url_to_publish
from base.tests.factories.academic_year import create_current_academic_year
from base.tests.factories.education_group_year import TrainingFactory, EducationGroupYearCommonFactory, \
    EducationGroupYearCommonBachelorFactory


@override_settings(ESB_API_URL="api.esb.com",
                   ESB_AUTHORIZATION="Basic dummy:1234", ESB_REFRESH_PEDAGOGY_ENDPOINT="offer/{year}/{code}/refresh",
                   ESB_REFRESH_COMMON_PEDAGOGY_ENDPOINT='offer/{year}/common/refresh',
                   ESB_REFRESH_COMMON_ADMISSION_ENDPOINT='offer/{year}/common_admission/refresh')
class TestPublishGeneralInformation(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.academic_year = create_current_academic_year()
        cls.training = TrainingFactory()

    @override_settings(ESB_REFRESH_PEDAGOGY_ENDPOINT=None)
    def test_publish_case_missing_settings(self):
        with self.assertRaises(ImproperlyConfigured):
            general_information.publish(self.training)

    @mock.patch('threading.Thread')
    def test_publish_call_seperate_thread(self, mock_thread):
        mock_thread.start.return_value = True
        general_information.publish(self.training)
        self.assertTrue(mock_thread.start)

    @mock.patch('requests.get', return_value=HttpResponseNotFound)
    def test_publish_case_not_found_return_false(self, mock_requests):
        response = general_information._publish(self.training)
        self.assertIsInstance(response, bool)
        self.assertFalse(response)

    @mock.patch('requests.get', side_effect=Timeout)
    def test_publish_case_timout_reached(self, mock_requests):
        with self.assertRaises(PublishException):
            general_information._publish(self.training)

    @mock.patch('requests.get', return_value=HttpResponse)
    def test_publish_case_success(self, mock_requests):
        response = general_information._publish(self.training)
        self.assertIsInstance(response, bool)
        self.assertTrue(response)


class TestBulkPublish(TestCase):
    @mock.patch('base.business.education_groups.general_information._publish', return_value=True)
    def test_bulk_publish(self, mock_publish):
        training_1 = TrainingFactory()
        training_2 = TrainingFactory()

        result = _bulk_publish([training_1, training_2])
        self.assertIsInstance(result, list)
        self.assertListEqual(result, [True, True])


@override_settings(ESB_API_URL="api.esb.com",
                   ESB_REFRESH_PEDAGOGY_ENDPOINT="offer/{year}/{code}/refresh",
                   ESB_REFRESH_COMMON_PEDAGOGY_ENDPOINT='offer/{year}/common/refresh',
                   ESB_REFRESH_COMMON_ADMISSION_ENDPOINT='offer/{year}/common_admission/refresh')
class TestGetUrlToPublish(TestCase):
    def test_get_publish_url_case_is_common_of_common(self):
        common = EducationGroupYearCommonFactory()
        expected_url = "{api_url}/{endpoint}".format(
            api_url=settings.ESB_API_URL,
            endpoint=settings.ESB_REFRESH_COMMON_PEDAGOGY_ENDPOINT.format(year=common.academic_year.year),
        )

        self.assertEqual(expected_url, _get_url_to_publish(common))

    def test_get_publish_url_case_common_type(self):
        bachelor_common = EducationGroupYearCommonBachelorFactory()
        expected_url = "{api_url}/{endpoint}".format(
            api_url=settings.ESB_API_URL,
            endpoint=settings.ESB_REFRESH_COMMON_ADMISSION_ENDPOINT.format(year=bachelor_common.academic_year.year),
        )

        self.assertEqual(expected_url, _get_url_to_publish(bachelor_common))

    def test_get_publish_url_case_not_common(self):
        training = TrainingFactory()
        expected_url = "{api_url}/{endpoint}".format(
            api_url=settings.ESB_API_URL,
            endpoint=settings.ESB_REFRESH_PEDAGOGY_ENDPOINT.format(
                year=training.academic_year.year,
                code=training.acronym
            ),
        )
        self.assertEqual(expected_url, _get_url_to_publish(training))
