##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2017 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.utils.translation import gettext_lazy as _
from django.views.generic import UpdateView

from program_management.forms.group_element_year import GroupElementYearForm
from program_management.views import perms as group_element_year_perms
from program_management.views.generic import GenericGroupElementYearMixin


class UpdateGroupElementYearView(GenericGroupElementYearMixin, UpdateView):
    # UpdateView
    form_class = GroupElementYearForm
    template_name = "group_element_year/group_element_year_comment_inner.html"

    rules = [group_element_year_perms.can_update_group_element_year]

    def _call_rule(self, rule):
        return rule(self.request.user, self.get_object())

    # SuccessMessageMixin
    def get_success_message(self, cleaned_data):
        return _("The link of %(acronym)s has been updated") % {'acronym': self.object.child}

    def get_success_url(self):
        # We can just reload the page
        return
