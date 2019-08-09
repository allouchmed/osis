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
from django.db.models import Q, Prefetch, Count, Value, CharField
from django.db.models.functions import Concat
from django.utils.translation import ugettext_lazy as _

from assessments.business import scores_responsible as business_scores_responsible
from attribution.models.attribution import Attribution
from base.models.learning_unit_year import LearningUnitYear


class ScoresResponsibleFilter(django_filters.FilterSet):
    acronym = django_filters.CharFilter(
        field_name='acronym',
        lookup_expr='icontains',
        label=_('Acronym'),
    )
    learning_unit_title = django_filters.CharFilter(
        field_name='full_title',
        lookup_expr='icontains',
        label=_('Learning unit title'),
    )
    tutor = django_filters.CharFilter(
        method='filter_tutor',
        label=_('Tutor'),
    )
    scores_responsible = django_filters.CharFilter(
        method='filter_score_responsible',
        label=_('Scores responsible title'),
    )

    def filter_tutor(self, queryset, name, value):
        return queryset.filter(Q(attribution__tutor__person__first_name__icontains=value)
                               | Q(attribution__tutor__person__last_name__icontains=value))

    def filter_score_responsible(self, queryset, name, value):
        return queryset.filter(Q(attribution__tutor__person__first_name__icontains=value) |
                               Q(attribution__tutor__person__last_name__icontains=value),
                               attribution__score_responsible=True)

    class Meta:
        model = LearningUnitYear
        fields = ['acronym', 'learning_unit_title', 'tutor', 'scores_responsible']

    def __init__(self, academic_year, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.academic_year = academic_year

    def filter_queryset(self, queryset):
        queryset = queryset.filter(
            academic_year=self.academic_year
        ).annotate(
            attributions_count=Count('attribution'),
            full_title=Concat(
                'learning_container_year__common_title', Value(' - '), 'specific_title',
                output_field=CharField()
            )
        )
        queryset = business_scores_responsible.filter_learning_unit_year_according_person(
            queryset,
            self.request.user.person,
        )
        queryset = super().filter_queryset(queryset)

        return queryset.select_related('learning_container_year')\
            .prefetch_related(
                Prefetch(
                    'attribution_set',
                    queryset=Attribution.objects.all().select_related('tutor__person')
                    .order_by('-score_responsible', 'tutor__person__last_name', 'tutor__person__first_name')
                )
        )
