##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2020 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import BaseCommand

from osis_role import role


class Command(BaseCommand):
    help = 'Synchronize all declared osis-roles (=groups) with user in table which are defined in OsisRoleManager'

    def handle(self, *args, **options):
        user_mdl = get_user_model()
        for role_mdl in role.role_manager.roles:
            group, _ = Group.objects.get_or_create(name=role_mdl.group_name)

            user_ids = role_mdl.objects.exclude(person__user__isnull=True).values_list('person__user_id', flat=True)
            for user_id in user_ids:
                user = user_mdl.objects.get(pk=user_id)
                user.groups.add(group)

            users_to_delink = user_mdl.objects.filter(groups__name=role_mdl.group_name).exclude(pk__in=user_ids)
            for user in users_to_delink:
                user.groups.remove(group)

            self.stdout.write(self.style.SUCCESS('Role {} successfully synchronized'.format(role_mdl.group_name)))
