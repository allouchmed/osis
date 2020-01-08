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
import rules
from django.contrib import admin
from django.db import models
from django.utils.translation import gettext_lazy as _

from osis_role.contrib import models as osis_role_models
from learning_unit.perms.rules import is_link_to_management_entity
from base.models import entity


class FacultyManagerLearningUnitAdmin(admin.ModelAdmin):
    list_display = ('person', 'entity', 'with_child')
    search_fields = ['person__first_name', 'person__last_name']
    raw_id_fields = ('person', 'entity',)


class FacultyManagerLearningUnit(osis_role_models.RoleModel):
    entity = models.ForeignKey(entity.Entity, on_delete=models.CASCADE)
    with_child = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("Faculty manager for learning unit year")
        verbose_name_plural = _("Faculty managers for learning unit year")
        group_name = "faculty_manager_for_ue"

    @classmethod
    def rule_set(cls):
        return rules.RuleSet({
            'view_learningunit': rules.always_allow(),
            'add_learningunit': rules.always_allow(),
            'change_learningunit': is_link_to_management_entity,
            'delete_learningunit': is_link_to_management_entity,

            'view_educationgroup': rules.always_allow(),
            'add_educationgroup': rules.always_allow(),
            'change_educationgroup': rules.always_deny(),
            'delete_educationgroup': rules.always_deny(),
        })
