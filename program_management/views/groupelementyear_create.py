############################################################################
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
############################################################################
from django.core.exceptions import ObjectDoesNotExist, ValidationError, PermissionDenied
from django.db import IntegrityError
from django.http import JsonResponse
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView
from django.views.generic.base import TemplateView

from base.models.education_group_year import EducationGroupYear
from base.utils.cache import ElementCache
from base.views.common import display_warning_messages, display_error_messages
from program_management.business.group_element_years.attach import AttachEducationGroupYearStrategy, \
    AttachLearningUnitYearStrategy
from program_management.business.group_element_years.detach import DetachEducationGroupYearStrategy, \
    DetachLearningUnitYearStrategy
from program_management.business.group_element_years.management import extract_child
from program_management.forms.group_element_year import GroupElementYearForm
from program_management.views.generic import GenericGroupElementYearMixin
from base.views.education_groups import perms


class AttachCheckView(GenericGroupElementYearMixin, TemplateView):
    template_name = "group_element_year/group_element_year_attach_type_dialog_inner.html"
    rules = []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["messages"] = []

        try:
            perms.can_change_education_group(self.request.user, self.education_group_year)
        except PermissionDenied as e:
            context["messages"].append(str(e))

        try:
            data = extract_child(self.education_group_year, self.request)
            child = data['child_branch'] if data.get('child_branch') else data.get('child_leaf')
            strategy = AttachEducationGroupYearStrategy if isinstance(child, EducationGroupYear) else \
                AttachLearningUnitYearStrategy
            strategy(parent=self.education_group_year, child=child).is_valid()

            context['object_to_attach'] = child
            context['source_link'] = data.get('source_link')
            context['education_group_year_parent'] = self.education_group_year

        except ObjectDoesNotExist:
            warning_msg = _("Please cut or copy an item before attach it")
            context["messages"].append(warning_msg)
        except ValidationError as e:
            error_messages = []
            for msg in e.messages:
                msg_prefix = _("Element selected %(element)s") % {
                    "element": "{} - {}".format(child.academic_year, child.acronym)
                }
                error_messages.append("{}: {}".format(msg_prefix, msg))
            context["messages"].append(error_messages)

        return context

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse({"error_messages": context["messages"]})


class AttachTypeDialogView(GenericGroupElementYearMixin, TemplateView):
    template_name = "group_element_year/group_element_year_attach_type_dialog_inner.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            data = extract_child(self.education_group_year, self.request)
            child = data['child_branch'] if data.get('child_branch') else data.get('child_leaf')

            context['object_to_attach'] = child
            context['source_link'] = data.get('source_link')
            context['education_group_year_parent'] = self.education_group_year

        except ObjectDoesNotExist:
            warning_msg = _("Please cut or copy an item before attach it")
            display_warning_messages(self.request, warning_msg)
        return context


class CreateGroupElementYearView(GenericGroupElementYearMixin, CreateView):
    # CreateView
    form_class = GroupElementYearForm
    template_name = "group_element_year/group_element_year_comment_inner.html"

    def get_form_kwargs(self):
        """ For the creation, the group_element_year needs a parent and a child """
        kwargs = super().get_form_kwargs()

        try:
            data = extract_child(self.education_group_year, self.request)
            kwargs.update({
                'parent': self.education_group_year,
                'child_branch': data.get('child_branch'),
                'child_leaf': data.get('child_leaf')
            })

            child = kwargs['child_branch'] if kwargs['child_branch'] else kwargs['child_leaf']
            strategy = AttachEducationGroupYearStrategy if isinstance(child, EducationGroupYear) else \
                AttachLearningUnitYearStrategy
            strategy(parent=self.education_group_year, child=child).is_valid()
        except ObjectDoesNotExist:
            warning_msg = _("Please cut or copy an item before attach it")
            display_warning_messages(self.request, warning_msg)
        except ValidationError as e:
            display_error_messages(self.request, e.messages)
        except IntegrityError as e:
            warning_msg = str(e)
            display_warning_messages(self.request, warning_msg)

        return kwargs

    def form_valid(self, form):
        """
        If the form is valid, save the associated model.
        """
        # Clear cache.
        ElementCache(self.request.user).clear()
        return super().form_valid(form)

    # SuccessMessageMixin
    def get_success_message(self, cleaned_data):
        return _("The link of %(acronym)s has been created") % {'acronym': self.object.child}

    def get_success_url(self):
        """ We'll reload the page """
        return


class MoveGroupElementYearView(CreateGroupElementYearView):
    form_class = GroupElementYearForm
    template_name = "group_element_year/group_element_year_comment_inner.html"

    @cached_property
    def strategy(self):
        obj = self.get_object()
        strategy_class = DetachEducationGroupYearStrategy if obj.child_branch else DetachLearningUnitYearStrategy
        return strategy_class(obj)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        if not self.strategy.is_valid():
            display_error_messages(self.request, self.strategy.errors)

        return kwargs

    def form_valid(self, form):
        self.strategy.post_valid()
        obj = self.get_object()
        obj.delete()
        return super().form_valid(form)
