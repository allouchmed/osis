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
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django_filters.views import FilterView

from assessments.api.serializers.scores_responsible import ScoresResponsibleListSerializer
from assessments.forms.scores_responsible import ScoresResponsibleFilter
from attribution import models as mdl_attr
from attribution.business.score_responsible import get_attributions_data
from attribution.models.attribution import Attribution
from base import models as mdl_base
from base.models.learning_unit_year import LearningUnitYear
from base.utils.cache import CacheFilterMixin
from base.models.entity_manager import EntityManager
from base.models import entity_manager
from base.forms.academic_actor import AcademicActorFilter


class AcademicActorsSearch(LoginRequiredMixin, PermissionRequiredMixin, CacheFilterMixin, FilterView):
    model = LearningUnitYear
    paginate_by = 20
    template_name = "academic_actors/overview.html"

    filterset_class = AcademicActorFilter
    permission_required = entity_manager.get_perms(EntityManager)

    def get_filterset_kwargs(self, filterset_class):
        return {
            **super().get_filterset_kwargs(filterset_class)

        }

    def render_to_response(self, context, **response_kwargs):

        return super().render_to_response(context, **response_kwargs)
