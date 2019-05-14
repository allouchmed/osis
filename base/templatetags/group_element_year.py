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
from django import template
from django.core.exceptions import PermissionDenied

from base.business.group_element_years.perms import is_eligible_to_update_group_element_year
from base.templatetags.education_group import ICONS

register = template.Library()


def _get_permission(context, permission):
    permission_denied_message = ""
    group_element_year = context.get('group')
    person = context.get('person')
    root = context.get("root") or context.get("parent")

    try:
        result = permission(person, group_element_year, raise_exception=True)

    except PermissionDenied as e:
        result = False
        permission_denied_message = str(e)

    return permission_denied_message, "" if result else "disabled", root


@register.inclusion_tag("blocks/button/button_template.html", takes_context=True,
                        name='group_element_year_button_with_permission')
def button_with_permission(context, title, value, url):
    permission_denied_message, disabled, root = _get_permission(context, is_eligible_to_update_group_element_year)
    load_modal = True

    if disabled:
        title = permission_denied_message
        load_modal = False

    return {
        'load_modal': load_modal,
        'title': title,
        'class_button': "btn-default btn-sm " + disabled,
        'icon': ICONS[value],
        'url': url,
    }
