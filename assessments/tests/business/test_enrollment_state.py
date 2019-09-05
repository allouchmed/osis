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
import datetime

from django.test import TestCase

from base.tests.factories.academic_year import create_current_academic_year, AcademicYearFactory
from base.tests.factories.exam_enrollment import ExamEnrollmentFactory
from base.tests.factories.session_examen import SessionExamFactory
from base.models.enums import number_session, academic_calendar_type
from assessments.templatetags.enrollment_state import get_line_color
from assessments.business.enrollment_state import ENROLLED_LATE_COLOR, NOT_ENROLLED_COLOR
from base.models.enums import exam_enrollment_state as enrollment_states
from base.tests.factories.academic_calendar import AcademicCalendarFactory, AcademicCalendarExamSubmissionFactory
from base.tests.factories.session_exam_calendar import SessionExamCalendarFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory


class EnrollmentStateTests(TestCase):
    def setUp(self):
        self.academic_calendar = AcademicCalendarExamSubmissionFactory(
            title="Submission of score encoding - 1",
            academic_year__current=True
        )
        self.session_exam_calendar = SessionExamCalendarFactory(academic_calendar=self.academic_calendar,
                                                                number_session=number_session.ONE)
        self.session_exam = SessionExamFactory(
            number_session=number_session.ONE,
            learning_unit_year__academic_year__current=True
        )

    def test_get_line_color_not_enrolled(self):
        exam_enrollment = ExamEnrollmentFactory(session_exam=self.session_exam,
                                                enrollment_state=enrollment_states.NOT_ENROLLED)
        self.assertEqual(get_line_color(exam_enrollment), NOT_ENROLLED_COLOR)

    def test_get_line_color_enrolled_late(self):
        exam_enrollment = ExamEnrollmentFactory(
            session_exam=self.session_exam,
            enrollment_state=enrollment_states.ENROLLED,
            date_enrollment=self.academic_calendar.start_date + datetime.timedelta(days=1)
        )
        self.assertEqual(get_line_color(exam_enrollment), ENROLLED_LATE_COLOR)

    def test_get_line_color_enrolled(self):
        exam_enrollment = ExamEnrollmentFactory(
            session_exam=self.session_exam,
            enrollment_state=enrollment_states.ENROLLED,
            date_enrollment=self.academic_calendar.start_date - datetime.timedelta(days=1)
        )
        self.assertIsNone(get_line_color(exam_enrollment))
