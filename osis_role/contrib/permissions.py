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
from django.contrib.auth.backends import ModelBackend

from osis_role import role


class ObjectPermissionBackend(ModelBackend):
    def has_perm(self, user_obj, perm, *args, **kwargs):
        if not user_obj.is_active or user_obj.is_anonymous:
            return False

        results = set()
        for role_mdl in _get_roles_assigned(user_obj):
            qs = role_mdl.objects.filter(person=getattr(user_obj, 'person', None))
            if qs.exists():
                rule_set = role_mdl.rule_set()
                _add_role_queryset_to_perms_context(rule_set, perm, qs)
                results.add(rule_set.test_rule(perm, user_obj, *args, **kwargs))
        return any(results)  # //Fallback to previous model or super().has_perm(user_obj, perm, obj=kwargs.get('obj'))


def _get_roles_assigned(user_obj):
    groups_assigned = user_obj.groups.values_list('name', flat=True)
    return {r for r in role.role_manager.roles if r.group_name in groups_assigned}


def _add_role_queryset_to_perms_context(rule_set, perm, qs):
    """
    :param rule_set: Set of rules for a specific role
    :param perm: Django permission name
    :param qs: Queryset which represent the role found on database
    :return: rule_set with cached predicate
    """
    if perm in rule_set:
        @rules.predicate(name='cache_role_qs')
        def cache_role_qs_fn(*args, **kwargs):
            cache_role_qs_fn.context['role_qs'] = qs
            return True
        rule_set[perm] = cache_role_qs_fn & rule_set[perm]
    return rule_set

