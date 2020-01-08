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


class FacultyManagerAdmin(admin.ModelAdmin):
    list_display = ('person', 'entity', 'with_child')
    search_fields = ['person__first_name', 'person__last_name']
    raw_id_fields = ('person', 'entity',)


class FacultyManager(osis_role_models.RoleModel):
    entity = models.ForeignKey(entity.Entity, on_delete=models.CASCADE)
    with_child = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("Faculty manager")
        verbose_name_plural = _("Faculty managers")
        group_name = "faculty_manager"

    @classmethod
    def rule_set(cls):
        return rules.RuleSet({
            'base.can_access_learningunit': rules.always_allow,  # Todo: Use view_learningunit instead
            'base.view_learningunit': rules.always_allow,
            'base.add_learningunit': rules.always_allow,
            'base.can_create_learningunit': rules.always_allow,  # Todo: Use add_learningunit instead
            'base.change_learningunit': is_link_to_management_entity,
            'base.can_edit_learningunit': is_link_to_management_entity,  # Todo: Use change_learningunit instead
            'base.delete_learningunit': is_link_to_management_entity,
            'base.can_delete_learningunit': is_link_to_management_entity,  # Todo: Use delete_learningunit instead
            'base.can_access_externallearningunityear': rules.always_allow,
            'base.can_edit_learningunit_date': rules.always_allow,
            'base.can_edit_learningunit_pedagogy': rules.always_allow,
            'base.can_edit_learningunit_specification': rules.always_allow,
            'base.can_propose_learningunit': rules.always_allow,
            'base.delete_learningunityear': rules.always_allow,  # Todo: Use delete_learningunit instead
            'base.can_access_catalog': rules.always_allow,
            'base.is_institution_administrator': rules.always_allow,  # Todo remove this perms because it is a group, not a perms
            'base.add_proposalfolder': rules.always_allow,
            'base.change_proposalfolder': rules.always_allow,
            'base.delete_proposalfolder': rules.always_allow,
            'base.add_proposallearningunit': rules.always_allow,
            'base.can_edit_learning_unit_proposal': rules.always_allow,
            'base.change_proposallearningunit': rules.always_allow,
            'base.delete_proposallearningunit': rules.always_allow,
            'base.can_access_structure': rules.always_allow,
            'base.can_manage_charge_repartition': rules.always_allow,
            'base.can_manage_attribution': rules.always_allow,
            'base.change_admissioncondition': rules.always_allow,
            'base.view_educationgroup': rules.always_allow,
            'base.add_educationgroup': rules.always_allow,
            'base.change_educationgroup': is_link_to_management_entity,
            'base.delete_educationgroup': is_link_to_management_entity,
            'base.can_access_education_group': rules.always_allow,
            'base.change_pedagogyinformation': rules.always_allow,
            'base.add_educationgroupachievement': rules.always_allow,
            'base.change_educationgroupachievement': rules.always_allow,
            'base.delete_educationgroupachievement': rules.always_allow,
            'base.change_learningclassyear': rules.always_allow,
            'base.change_learningcomponentyear': rules.always_allow,
            'base.add_externallearningunityear': rules.always_allow,
        })
