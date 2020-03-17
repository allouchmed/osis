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
import itertools
from unittest import mock

from django.contrib import messages
from django.contrib.auth.models import Permission
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.utils.translation import gettext as _
from waffle.models import Flag
from waffle.testutils import override_flag

from base.business.learning_units.achievement import DELETE, DOWN, UP
from base.forms.learning_achievement import LearningAchievementEditForm
from base.models.enums import learning_unit_year_subtypes
from base.models.learning_achievement import LearningAchievement
from base.models.learning_unit_year import LearningUnitYear
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.entity_version import EntityVersionFactory
from base.tests.factories.learning_achievement import LearningAchievementFactory
from base.tests.factories.learning_component_year import LearningComponentYearFactory
from base.tests.factories.learning_container_year import LearningContainerYearFactory
from base.tests.factories.learning_unit import LearningUnitFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.person import PersonFactory, PersonWithPermissionsFactory
from base.tests.factories.person_entity import PersonEntityFactory
from base.tests.factories.proposal_learning_unit import ProposalLearningUnitFactory
from base.tests.factories.utils.get_messages import get_messages_from_response
from base.views.learning_achievement import management, create, create_first
from cms.tests.factories.text_label import TextLabelFactory
from reference.models.language import FR_CODE_LANGUAGE
from reference.tests.factories.language import LanguageFactory


@override_flag('learning_achievement_update', active=True)
class TestLearningAchievementView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.language_fr = LanguageFactory(code="FR")
        cls.language_en = LanguageFactory(code="EN")
        cls.person = PersonFactory()
        cls.person_entity = PersonEntityFactory(person=cls.person)

        cls.academic_year = AcademicYearFactory(current=True)
        cls.learning_unit_year = LearningUnitYearFactory(
            academic_year=cls.academic_year,
            subtype=learning_unit_year_subtypes.FULL,
            learning_container_year__requirement_entity=cls.person_entity.entity,
        )

        cls.achievement_en = LearningAchievementFactory(
            language=cls.language_en,
            learning_unit_year=cls.learning_unit_year,
            order=0
        )
        cls.reverse_learning_unit_yr = reverse('learning_unit', args=[cls.learning_unit_year.id])
        flag, created = Flag.objects.get_or_create(name='learning_achievement_update')
        flag.users.add(cls.person.user)
        cls.request_factory = RequestFactory()

    def setUp(self):
        self.achievement_fr = LearningAchievementFactory(
            language=self.language_fr,
            learning_unit_year=self.learning_unit_year,
            order=0,
            code_name=self.achievement_en.code_name
        )
        self.client.force_login(self.person.user)

    def test_operation_method_not_allowed(self):
        response = self.client.post(
            reverse('achievement_management', args=[self.achievement_fr.learning_unit_year.id]),
            data={'achievement_id': self.achievement_fr.id, 'action': DELETE}
        )
        with self.assertRaises(PermissionDenied):
            management(response.wsgi_request, self.achievement_fr.learning_unit_year.id)

    def test_delete_redirection(self):
        request = self.client.post(
            reverse('achievement_management', args=[self.achievement_fr.learning_unit_year.id]),
            data={'achievement_id': self.achievement_fr.id, 'action': DELETE}
        )

        self.person.user.user_permissions.add(Permission.objects.get(codename="can_access_learningunit"))
        self.person.user.user_permissions.add(Permission.objects.get(codename="can_create_learningunit"))
        request.wsgi_request.user = self.person.user
        response = management(request.wsgi_request, self.achievement_fr.learning_unit_year.id)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url,
                         "/learning_units/{}/specifications/".format(self.achievement_fr.learning_unit_year.id))

    def test_delete_permission_denied(self):
        self.person_entity.delete()
        response = self.client.post(reverse('achievement_management',
                                            args=[self.achievement_fr.learning_unit_year.id]),
                                    data={'achievement_id': self.achievement_fr.id,
                                          'action': DELETE})
        self.person.user.user_permissions.add(Permission.objects.get(codename="can_access_learningunit"))
        self.person.user.user_permissions.add(Permission.objects.get(codename="can_create_learningunit"))

        with self.assertRaises(PermissionDenied):
            management(response.wsgi_request, self.achievement_fr.learning_unit_year.id)

    def test_create_not_allowed(self):
        response = self.client.get(self.reverse_learning_unit_yr)

        with self.assertRaises(PermissionDenied):
            create(response.wsgi_request, self.learning_unit_year.id, self.achievement_fr.id)

        response = self.client.post(self.reverse_learning_unit_yr)

        with self.assertRaises(PermissionDenied):
            create(response.wsgi_request, self.learning_unit_year.id, self.achievement_fr.id)

    def test_create_first_not_allowed(self):
        response = self.client.get(self.reverse_learning_unit_yr)

        with self.assertRaises(PermissionDenied):
            create_first(response.wsgi_request, self.learning_unit_year.id)

        response = self.client.post(self.reverse_learning_unit_yr)

        with self.assertRaises(PermissionDenied):
            create_first(response.wsgi_request, self.learning_unit_year.id)

    def test_check_achievement_code(self):
        self.person.user.user_permissions.add(Permission.objects.get(codename="can_access_learningunit"))
        url = reverse('achievement_check_code', args=[self.learning_unit_year.id])
        response = self.client.get(url, data={'code': self.achievement_fr.code_name})
        self.assertEqual(type(response), JsonResponse)


class TestLearningAchievementActions(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.language_fr = LanguageFactory(code="FR")
        cls.language_en = LanguageFactory(code="EN")
        cls.person = PersonWithPermissionsFactory("can_access_learningunit", "can_create_learningunit")
        cls.superperson = PersonFactory(user__superuser=True)

        cls.person_entity = PersonEntityFactory(person=cls.superperson)

        cls.academic_year = AcademicYearFactory(current=True)
        AcademicYearFactory.produce_in_future(quantity=2)
        cls.luy = LearningUnitYearFactory(
            academic_year=cls.academic_year,
            subtype=learning_unit_year_subtypes.FULL,
            learning_container_year__requirement_entity=cls.person_entity.entity,
        )
        cls.future_luy = LearningUnitYearFactory(
            academic_year=cls.academic_year.next(),
            learning_unit=cls.luy.learning_unit,
        )
        cls.template_naem = 'learning_unit/achievement_edit.html'

    def setUp(self):
        self.client.force_login(self.superperson.user)

    def test_delete(self):
        achievements = [
            LearningAchievementFactory(language=lang, learning_unit_year=self.luy, consistency_id=consistency_id)
            for lang in [self.language_fr, self.language_en] for consistency_id in [1, 2]
        ]
        self.client.post(
            reverse('achievement_management', args=[self.luy.id]),
            data={'action': DELETE, 'achievement_id': achievements[0].id}
        )
        self.assertEqual(set(LearningAchievement.objects.all()), {achievements[1], achievements[3]})

    def test_up(self):
        achievements = [
            LearningAchievementFactory(code_name=code, language=lang, learning_unit_year=self.luy, consistency_id=code)
            for code in [1, 2] for lang in [self.language_fr, self.language_en]
        ]
        self.client.post(
            reverse('achievement_management', args=[self.luy.id]),
            data={'action': UP, 'achievement_id': achievements[2].id}
        )
        for achievement in LearningAchievement.objects.filter(consistency_id=1):
            self.assertEqual(achievement.order, 1)
        for achievement in LearningAchievement.objects.filter(consistency_id=2):
            self.assertEqual(achievement.order, 0)

    def test_down(self):
        achievements = [
            LearningAchievementFactory(code_name=code, language=lang, learning_unit_year=self.luy, consistency_id=code)
            for code in [1, 2] for lang in [self.language_fr, self.language_en]
        ]
        self.client.post(
            reverse('achievement_management', args=[self.luy.id]),
            data={'action': DOWN, 'achievement_id': achievements[0].id}
        )
        for achievement in LearningAchievement.objects.filter(consistency_id=1):
            self.assertEqual(achievement.order, 1)
        for achievement in LearningAchievement.objects.filter(consistency_id=2):
            self.assertEqual(achievement.order, 0)

    def test_learning_achievement_edit(self):
        learning_achievement = LearningAchievementFactory(learning_unit_year=self.luy)
        response = self.client.get(
            reverse('achievement_edit', args=[self.luy.id, learning_achievement.id]),
            data={'achievement_id': learning_achievement.id}
        )
        self.assertTemplateUsed(response, self.template_naem)
        self.assertIsInstance(response.context['form'], LearningAchievementEditForm)

    def test_learning_achievement_simple_save(self):
        msg = self._test_learning_achievement_save()
        self.assertEqual(msg[0].get('message'), "{}.".format(_("The learning unit has been updated")))
        self.assertEqual(msg[0].get('level'), messages.SUCCESS)

    def test_learning_achievement_save_with_proposal(self):
        ProposalLearningUnitFactory(learning_unit_year=self.luy)
        msg = self._test_learning_achievement_save()
        expected_msg = "{}. {}.".format(
            _("The learning unit has been updated"),
            _("The learning unit is in proposal, the report from %(proposal_year)s will be done at consolidation") % {
                'proposal_year': self.luy.proposallearningunit.learning_unit_year.academic_year
            }
        )
        self.assertEqual(msg[0].get('message'), expected_msg)
        self.assertEqual(msg[0].get('level'), messages.SUCCESS)

    def _test_learning_achievement_save(self):
        learning_achievement = LearningAchievementFactory(
            learning_unit_year=self.luy,
            language=self.language_fr
        )
        learning_achievement_en = LearningAchievementFactory(
            learning_unit_year=self.luy,
            language=self.language_en
        )
        response = self.client.post(reverse(
            'achievement_edit',
            kwargs={
                'learning_unit_year_id': self.luy.id,
                'learning_achievement_id': learning_achievement.id
            }
        ),
            data={
                'code_name': 'AA1',
                'text_fr': 'Text',
                'lua_fr_id': learning_achievement.id,
                'lua_en_id': learning_achievement_en.id,
                'postpone': 0
            }
        )
        self.assertEqual(response.status_code, 200)
        msg = get_messages_from_response(response)
        return msg

    @mock.patch("cms.models.translated_text.update_or_create")
    def test_learning_achievement_save_triggers_cms_save(self, mock_translated_text_update_or_create):
        learning_achievement = LearningAchievementFactory(
            code_name=1,
            learning_unit_year=self.luy,
            language=self.language_fr,
            consistency_id=1
        )
        LearningAchievementFactory(
            code_name=1,
            learning_unit_year=self.luy,
            language=self.language_en,
            consistency_id=1
        )
        TextLabelFactory(label='themes_discussed')

        self.client.post(reverse(
            'achievement_edit',
            kwargs={
                'learning_unit_year_id': self.luy.id,
                'learning_achievement_id': learning_achievement.id
            }
        ),
            data={
                'code_name': 'AA1',
                'text_fr': 'Text',
                'postpone': 0,
                'consistency_id': 1,
            }
        )
        self.assertTrue(mock_translated_text_update_or_create.called)

    def test_learning_achievement_create(self):
        achievement_fr = LearningAchievementFactory(language=self.language_fr, learning_unit_year=self.luy)
        response = self.client.get(
            reverse('achievement_create', args=[self.luy.id, achievement_fr.id]),
            data={'language_code': self.language_fr.code}
        )
        self.assertTemplateUsed(response, self.template_naem)
        context = response.context
        self.assertIsInstance(context['form'], LearningAchievementEditForm)
        self.assertEqual(context['learning_unit_year'], self.luy)
        self.assertEqual(context['language_code'], self.language_fr.code)
        self.assertTrue(context['create'], self.language_fr.code)

    def test_learning_achievement_create_existing_learning_achievement_in_future(self):
        achievement_fr = LearningAchievementFactory(language=self.language_fr, learning_unit_year=self.luy)
        future_achievement_fr = LearningAchievementFactory(
            language=self.language_fr,
            learning_unit_year=self.future_luy,
            consistency_id=achievement_fr.consistency_id + 1
        )
        response = self.client.get(
            reverse('achievement_create', args=[self.luy.id, achievement_fr.id]),
            data={'language_code': self.language_fr.code}
        )
        self.assertTemplateUsed(response, self.template_naem)
        self.assertIsInstance(response.context['form'], LearningAchievementEditForm)
        self.assertEqual(response.context['form'].consistency_id, future_achievement_fr.consistency_id + 1)

    def test_learning_achievement_create_first(self):
        response = self.client.get(reverse('achievement_create_first', args=[self.luy.id]),
                                   data={'language_code': FR_CODE_LANGUAGE})

        self.assertTemplateUsed(response, self.template_naem)
        context = response.context
        self.assertIsInstance(context['form'], LearningAchievementEditForm)
        self.assertEqual(context['learning_unit_year'], self.luy)
        self.assertEqual(context['language_code'], FR_CODE_LANGUAGE)

    def test_learning_achievement_create_first_existing_learning_achievement_in_future(self):
        future_achievement = LearningAchievementFactory(learning_unit_year=self.future_luy)
        response = self.client.get(reverse('achievement_create_first', args=[self.luy.id]))
        self.assertTemplateUsed(response, self.template_naem)
        self.assertIsInstance(response.context['form'], LearningAchievementEditForm)
        self.assertEqual(response.context['form'].consistency_id, future_achievement.consistency_id + 1)


class TestLearningAchievementPostponement(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.language_fr = LanguageFactory(code="FR")
        cls.language_en = LanguageFactory(code="EN")
        cls.person = PersonWithPermissionsFactory("can_access_learningunit", "can_create_learningunit")
        cls.person_entity = PersonEntityFactory(person=cls.person)
        flag, created = Flag.objects.get_or_create(name='learning_achievement_update')
        flag.users.add(cls.person.user)
        EntityVersionFactory(entity=cls.person_entity.entity)
        cls.academic_years = AcademicYearFactory.produce_in_future(quantity=5)
        cls.max_la_number = 2 * len(cls.academic_years)
        cls.learning_unit = LearningUnitFactory(start_year=cls.academic_years[0], end_year=cls.academic_years[-1])
        cls.learning_unit_years = [LearningUnitYearFactory(
            academic_year=academic_year,
            subtype=learning_unit_year_subtypes.FULL,
            learning_container_year=LearningContainerYearFactory(
                academic_year=academic_year,
                requirement_entity=cls.person_entity.entity
            ),
            learning_unit=cls.learning_unit,
            acronym="TEST0000"
        ) for academic_year in cls.academic_years]
        cls.learning_component_years = [LearningComponentYearFactory(
            learning_unit_year=luy,
        ) for luy in cls.learning_unit_years]

    def setUp(self):
        self.client.force_login(self.person.user)
        self.create_response = self._create_achievements()

    def test_learning_achievement_create_with_postponement(self):
        self.assertEqual(self.create_response.status_code, 200)
        for achievement in LearningAchievement.objects.filter(language__code=FR_CODE_LANGUAGE):
            self.assertEqual(achievement.text, 'text')

    def test_learning_achievement_deletion_with_postponement(self):
        achievement = LearningAchievement.objects.filter(
            learning_unit_year=self.learning_unit_years[0],
            language__code=FR_CODE_LANGUAGE
        ).first()
        operation_url = reverse('achievement_management', args=[self.learning_unit_years[0].id])
        self.client.post(operation_url, data={
            'achievement_id': achievement.id,
            'action': DELETE
        })
        self.assertFalse(LearningAchievement.objects.all().exists())

    def test_learning_achievement_move_up_with_postponement(self):
        self._create_ordered_achievements([2])
        self._move_achievement(consistency_id=2, operation=UP)
        self.assertEqual(LearningAchievement.objects.filter(consistency_id=1, order=1).count(), self.max_la_number)
        self.assertEqual(LearningAchievement.objects.filter(consistency_id=2, order=0).count(), self.max_la_number)

    def test_learning_achievement_move_down_with_postponement(self):
        self._create_ordered_achievements([2])
        self._move_achievement(consistency_id=1, operation=DOWN)
        self.assertEqual(LearningAchievement.objects.filter(consistency_id=1, order=1).count(), self.max_la_number)
        self.assertEqual(LearningAchievement.objects.filter(consistency_id=2, order=0).count(), self.max_la_number)

    def test_learning_achievement_stop_postponement_when_future_order_is_different(self):
        self._create_ordered_achievements([2])
        last_postponed_luy = self.learning_unit_years[-1]
        for la in LearningAchievement.objects.filter(order=0, learning_unit_year=self.learning_unit_years[-1]):
            la.to(1)
        response = self._move_achievement(consistency_id=1, operation=DOWN)
        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertIn(str(last_postponed_luy.academic_year), str(messages_list[0]))

    def test_no_learning_unit_year_is_created_after_postponement(self):
        self.learning_unit_years.pop().delete()
        self.learning_component_years.pop().delete()
        self.assertEqual(self.create_response.status_code, 200)
        self.assertFalse(LearningUnitYear.objects.filter(academic_year=self.academic_years[-1]).exists())

    def _create_achievements(self):
        create_url = reverse('achievement_create_first', args=[self.learning_unit_years[0].id])
        create_response = self.client.post(create_url, data={
            'language_code': FR_CODE_LANGUAGE,
            'text_fr': 'text',
            'postpone': '1',
            'consistency_id': 1,
            'order': 0
        })
        return create_response

    def _create_ordered_achievements(self, ids):
        for luy, id, lang in itertools.product(self.learning_unit_years, ids, [self.language_fr, self.language_en]):
            LearningAchievementFactory(consistency_id=id, learning_unit_year=luy, language=lang, order=id - 1)

    def _move_achievement(self, consistency_id, operation):
        operation_url = reverse('achievement_management', args=[self.learning_unit_years[0].id])
        achievement_to_move = LearningAchievement.objects.get(
            consistency_id=consistency_id,
            learning_unit_year=self.learning_unit_years[0],
            language=self.language_fr
        )
        return self.client.post(operation_url, data={
            'achievement_id': achievement_to_move.id,
            'action': operation
        })
