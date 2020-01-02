##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2018 Université catholique de Louvain (http://www.uclouvain.be)
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
import django_filters
from django import forms
from django.db.models import Q, Prefetch, Value, CharField, OuterRef, Subquery, When, Case
from django.db.models.functions import Concat
from django.utils.translation import gettext_lazy as _

from assessments.business import scores_responsible as business_scores_responsible
from attribution.models.attribution import Attribution
from base.models.entity_version import EntityVersion
from base.models.learning_unit_year import LearningUnitYear
from django_filters import FilterSet, filters, OrderingFilter
from django.utils.translation import gettext_lazy as _, pgettext_lazy
from django.contrib.auth.models import Group
from base.models.entity_manager import EntityManager, find_by_user, find_entities_with_descendants_from_entity_managers
from django.db.models import QuerySet, Q

from base.models import entity_manager, program_manager, entity_version
from base.models.person import Person


class EntityModelChoiceField(filters.ModelChoiceFilter):
    def label_from_instance(self, obj):
        print('*****')
        return obj.entity.most_recent_acronym


class AcademicActorFilter(django_filters.FilterSet):

    roles = filters.ModelChoiceFilter(
        queryset=Group.objects.all(),
        required=False,
        label=_('Role'),
        empty_label=pgettext_lazy("plural", "All"),
    )
    entities = filters.ModelMultipleChoiceFilter(
        queryset=None,
        required=False,
        label=_('Entities'),
    )
    # entities_selected = filters.ModelMultipleChoiceFilter(
    #     queryset=None,
    #     required=False,
    #     label=_('Entities'),
    # )

    class Meta:
        fields = ['entities']

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.user = self.request.user
        e = find_by_user(self.user)
        user_entities = find_by_user(self.user)
        self.filters['entities'].queryset = user_entities

        dict = {}
        structure = entity_version.build_current_entity_version_structure_in_memory()
        for e in user_entities:
            j = EntityManager.objects.filter(id=e.id)
            entities_with_descendants = find_entities_with_descendants_from_entity_managers(j, structure)
            dict.update({e.entity: entities_with_descendants})
        # print(type(entities_with_descendants))
        # print(entities_with_descendants)
        print(dict)
        # self.filters['entities'].queryset = entities_with_descendants
        self.filters['entities'].field.label_from_instance = lambda obj: obj.entity.most_recent_acronym

    def filter_queryset(self, queryset):
        return None
