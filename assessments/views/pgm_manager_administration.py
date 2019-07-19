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
import itertools
import json
from collections import OrderedDict

from dal import autocomplete
from django import forms
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DeleteView, FormView
from django.views.generic.edit import BaseUpdateView

from base import models as mdl
from base.models.education_group_year import EducationGroupYear
from base.models.entity_manager import is_entity_manager, has_perm_entity_manager
from base.models.offer_type import OfferType
from base.models.person import Person
from base.models.program_manager import ProgramManager
from base.views.mixins import AjaxTemplateMixin

ALL_OPTION_VALUE = "-"
ALL_OPTION_VALUE_ENTITY = "all_"

EXCLUDE_OFFER_TYPE_SEARCH = ('Master approfondi', "Master didactique", "Master spécialisé")


class ProgramManagerListView(ListView):
    model = ProgramManager
    template_name = "admin/programmanager_list.html"

    def get_queryset(self):
        qs = super().get_queryset()
        education_group_years = self.request.GET.getlist('education_group_year')
        if not education_group_years:
            return qs.none()

        return qs.filter(education_group__educationgroupyear__in=education_group_years).order_by(
            'person__last_name', 'person__first_name', 'pk'
        ).select_related('person')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['education_group_years'] = self.request.GET.getlist('education_group_year')

        result = OrderedDict()
        for i in self.object_list:
            result.setdefault(i.person, []).append(i)

        context["by_person"] = result
        return context


class ProgramManagerMixin(UserPassesTestMixin, AjaxTemplateMixin):
    model = ProgramManager
    success_url = reverse_lazy('manager_list')
    partial_reload = '#pnl_managers'

    def test_func(self):
        return is_entity_manager(self.request.user)

    @property
    def education_group_years(self) -> list:
        return self.request.GET['education_group_year'].split(',')

    def get_success_url(self):
        url = reverse_lazy('manager_list') + "?"
        for oy in self.education_group_years:
            url += "egy={}&".format(oy)
        return url


class ProgramManagerDeleteView(ProgramManagerMixin, DeleteView):
    template_name = 'admin/programmanager_confirm_delete_inner.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['manager'] = self.object.person
        context['other_programs'] = self.object.person.programmanager_set.exclude(pk=self.object.pk)
        return context


class ProgramManagerPersonDeleteView(ProgramManagerMixin, DeleteView):
    template_name = 'admin/programmanager_confirm_delete_inner.html'

    def get_object(self, queryset=None):
        return self.model.objects.filter(
            person__pk=self.kwargs['pk'],
            education_group__educationgroupyear__in=self.education_group_years
        )

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        for obj in self.object.all():
            obj.delete()
        return self._ajax_response() or HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        manager = Person.objects.get(pk=self.kwargs['pk'])
        context['manager'] = manager
        context['other_programs'] = manager.programmanager_set.exclude(
            education_group__educationgroupyear__in=self.education_group_years
        )
        return context


class MainProgramManagerUpdateView(ProgramManagerMixin, BaseUpdateView):
    fields = 'is_main',


class MainProgramManagerPersonUpdateView(ProgramManagerMixin, ListView):
    def get_queryset(self):
        return self.model.objects.filter(
            person=self.kwargs["pk"],
            education_group__educationgroupyear__in=self.education_group_years
        )

    def post(self, *args, **kwargs):
        """ Update column is_main for selected offer_years"""
        val = json.loads(self.request.POST.get('is_main'))
        self.get_queryset().update(is_main=val)
        return super()._ajax_response() or HttpResponseRedirect(self.get_success_url())


class PersonAutocomplete(autocomplete.Select2QuerySetView):
    def get_result_label(self, item):
        return "{} {}, {}".format(item.last_name, item.first_name, item.email)

    def get_queryset(self):
        qs = Person.objects.all()
        if self.q:
            qs = qs.filter(Q(last_name__icontains=self.q) | Q(first_name__icontains=self.q))
        return qs.order_by('last_name', 'first_name')


class ProgramManagerForm(forms.ModelForm):
    class Meta:
        model = ProgramManager
        fields = ('person',)
        widgets = {'person': autocomplete.ModelSelect2(url='person-autocomplete', attrs={'style': 'width:100%'})}


class ProgramManagerCreateView(ProgramManagerMixin, FormView):
    form_class = ProgramManagerForm
    template_name = 'admin/manager_add_inner.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['education_group_years'] = self.request.GET['education_group_year']
        return context

    def form_valid(self, form):
        education_group_years = EducationGroupYear.objects.filter(pk__in=self.education_group_years)

        person = form.cleaned_data['person']
        for egy in education_group_years:
            ProgramManager.objects.get_or_create(
                person=person,
                education_group=egy.education_group,
                offer_year=egy.equivalent_offer_year
            )

        return super().form_valid(form)


@login_required
@user_passes_test(has_perm_entity_manager)
def pgm_manager_administration(request):
    administrator_entities = get_administrator_entities(request.user)
    current_academic_yr = mdl.academic_year.current_academic_year()
    return render(request, "admin/pgm_manager.html", {
        'academic_year': current_academic_yr,
        'administrator_entities_string': _get_administrator_entities_acronym_list(administrator_entities),
        'entities_managed_root': administrator_entities,
        'offer_types': OfferType.objects.exclude(name__in=EXCLUDE_OFFER_TYPE_SEARCH),
        'managers': _get_entity_program_managers(administrator_entities, current_academic_yr),
        'init': '1'})


@login_required
def pgm_manager_search(request):
    person_id = get_filter_value(request, 'person')
    manager_person = None
    if person_id:
        manager_person = get_object_or_404(Person, pk=person_id)

    entity_selected_id = get_filter_value(request, 'entity')  # if an acronym is selected this value is not none
    entity_root_selected = None  # if an 'all hierarchy of' is selected this value is not none

    if entity_selected_id is None:
        entity_root_selected = get_entity_root_selected(request)

    pgm_offer_type = get_filter_value(request, 'offer_type')

    administrator_entities = get_administrator_entities(request.user)

    current_academic_yr = mdl.academic_year.current_academic_year()

    data = {
        'academic_year': current_academic_yr,
        'person': manager_person,
        'administrator_entities_string': _get_administrator_entities_acronym_list(administrator_entities),
        'entities_managed_root': administrator_entities,
        'entity_selected': entity_selected_id,
        'entity_root_selected': entity_root_selected,
        'offer_types': OfferType.objects.exclude(name__in=EXCLUDE_OFFER_TYPE_SEARCH),
        'pgms': _get_programs(current_academic_yr,
                              get_entity_list(entity_selected_id, administrator_entities),
                              manager_person,
                              pgm_offer_type),
        'managers': _get_entity_program_managers(administrator_entities, current_academic_yr),
        'offer_type': pgm_offer_type
    }
    return render(request, "admin/pgm_manager.html", data)


def get_entity_root_selected(request):
    entity_root_selected = get_filter_value_entity(request, 'entity')
    if entity_root_selected is None:
        entity_root_selected = request.POST.get('entity_root', None)
    return entity_root_selected


def get_entity_list(entity_id, administrator_entities):
    if entity_id:
        entity_found = mdl.entity_version.find_by_id(entity_id)
        if entity_found:
            return [entity_found.entity]
    else:
        entity_versions = list(itertools.chain.from_iterable(
            (struct["children"] for struct in administrator_entities)
        ))
        return [ev.entity for ev in entity_versions]
    return None


@login_required
def get_filter_value(request, value_name):
    value = _get_request_value(request, value_name)

    if value == ALL_OPTION_VALUE or value == '' or value.startswith(ALL_OPTION_VALUE_ENTITY):
        return None
    return value


def get_administrator_entities(a_user):
    structures = []
    for entity_managed in mdl.entity_manager.find_by_user(a_user):
        root_version = entity_managed.entity.get_latest_entity_version()
        structures.append({'root': root_version,
                           'children': list(root_version.children) + [root_version]})
    return structures


def _get_programs(academic_yr, entity_list, manager_person, an_offer_type):
    qs = EducationGroupYear.objects.filter(
        academic_year=academic_yr,
        management_entity__in=entity_list
    )

    # FIXME Use educationgrouptype
    # if an_offer_type:
    #     qs = qs.filter(offer_type=an_offer_type)

    if manager_person:
        qs = qs.filter(education_group__programmanager__person=manager_person)
    return qs.distinct()


def _get_entity_program_managers(entity, academic_yr):
    root_entities = [struct["root"] for struct in entity]
    ordered_root_entities = sorted(root_entities, key=lambda entity_version: entity_version.acronym)

    return mdl.program_manager.find_by_management_entity([ev.entity for ev in ordered_root_entities], academic_yr)


def find_values(key_value, json_repr):
    results = []

    def _decode_dict(a_dict):
        try:
            results.append(a_dict[key_value])
        except KeyError:
            pass
        return a_dict

    json.loads(json_repr, object_hook=_decode_dict)  # return value ignored
    return results


@login_required
def get_filter_value_entity(request, value_name):
    value = _get_request_value(request, value_name)
    if value != '' and value.startswith(ALL_OPTION_VALUE_ENTITY):
        return value.replace(ALL_OPTION_VALUE_ENTITY, "")

    return None


def _get_request_value(request, value_name):
    if request.method == 'POST':
        value = request.POST.get(value_name, None)
    else:
        value = request.GET.get(value_name, None)
    return value


def _get_administrator_entities_acronym_list(administrator_entities):
    """
    Return a list of acronyms separated by comma.  List of the acronyms administrate by the user
    :param administrator_entities:
    :return:
    """
    return ', '.join(str(entity_manager['root'].acronym) for entity_manager in administrator_entities)
