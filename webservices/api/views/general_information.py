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
from django.db.models import Q, Value, CharField, OuterRef, Subquery
from django.shortcuts import get_object_or_404
from rest_framework import generics

from base.business.education_groups import general_information_sections
from base.models.education_group_year import EducationGroupYear
from base.models.enums.education_group_types import GroupType
from base.models.group_element_year import GroupElementYear
from cms.models.translated_text import TranslatedText
from cms.models.translated_text_label import TranslatedTextLabel
from program_management.business.group_element_years import group_element_year_tree
from webservices.api.serializers.general_information import GeneralInformationSerializer


class GeneralInformation(generics.RetrieveAPIView):
    """
        Return the general informations for an Education Group Year
    """
    name = 'generalinformations_read'
    serializer_class = GeneralInformationSerializer

    def get_object(self):
        egy = get_object_or_404(
            EducationGroupYear.objects.select_related(
                'academic_year',
                'admissioncondition',
                'education_group_type'
            ).prefetch_related(
                'educationgrouppublicationcontact_set',
                'educationgroupachievement_set'
            ),
            Q(acronym__iexact=self.kwargs['acronym']) | Q(partial_acronym__iexact=self.kwargs['acronym']),
            academic_year__year=self.kwargs['year'],
            education_group_type__name__in=general_information_sections.SECTIONS_PER_OFFER_TYPE.keys()
        )

        pertinent_sections = general_information_sections.SECTIONS_PER_OFFER_TYPE[egy.education_group_type.name]
        egy_queryset = EducationGroupYear.objects.filter(id=egy.id)
        self.extra_intro_offers = self._get_intro_offers(egy)
        common_egy = EducationGroupYear.objects.get_common(
            academic_year=egy.academic_year
        )
        translated_text_labels = TranslatedTextLabel.objects.filter(
            text_label__label=OuterRef('text_label__label'),
            language=self.kwargs['language'],
        ).values('label')[:1]
        translated_texts = TranslatedText.objects.filter(
            reference__in=[egy.id, common_egy.id],
            text_label__label__in=list(set(pertinent_sections['specific']).union(set(pertinent_sections['common']))),
            language=self.kwargs['language']
        ).annotate(
            translated_label=Subquery(translated_text_labels, output_field=CharField())
        )
        for label in pertinent_sections['common']:
            egy_queryset = egy_queryset.annotate(**{
                'common_' + label: Subquery(
                    translated_texts.filter(text_label__label=label, reference=common_egy.id).values('text')[:1],
                    output_field=CharField()
                ),
                'common_' + label + '_label': Subquery(
                    translated_texts.filter(
                        text_label__label=label,
                        reference=common_egy.id
                    ).values('translated_label')[:1],
                    output_field=CharField()
                )
            })
        for label in pertinent_sections['specific']:
            egy_queryset = egy_queryset.annotate(**{
                label: Subquery(
                    translated_texts.filter(text_label__label=label, reference=egy.id).values('text')[:1],
                    output_field=CharField()
                ),
                label + '_label': Subquery(
                    translated_texts.filter(text_label__label=label, reference=egy.id).values('translated_label')[:1],
                    output_field=CharField()
                )
            })

        intro_texts = TranslatedText.objects.filter(
            reference__in=[egy_item.id for egy_item in self.extra_intro_offers],
            text_label__label='intro',
            language=self.kwargs['language']
        ).annotate(
            partial_acronym=Subquery(
                EducationGroupYear.objects.filter(
                    id__in=[egy.id for egy in self.extra_intro_offers if egy.id == OuterRef('reference')]
                ).values('partial_acronym')[:1]
            )
        )

        for itt in intro_texts:
            egy_queryset = egy_queryset.annotate(**{
                'intro-' + itt.partial_acronym: Value(itt.text, output_field=CharField()) or None,
            })

        return egy_queryset.first()

    def get_serializer_context(self):
        serializer_context = super().get_serializer_context()
        serializer_context['language'] = self.kwargs['language']
        serializer_context['acronym'] = self.kwargs['acronym']
        serializer_context['intro_offers'] = [egy.partial_acronym for egy in self.extra_intro_offers]
        return serializer_context

    @staticmethod
    def _get_intro_offers(obj):
        hierarchy = group_element_year_tree.EducationGroupHierarchy(root=obj)
        extra_intro_offers = hierarchy.get_finality_list() + hierarchy.get_option_list()
        common_core = GroupElementYear.objects.select_related('child_branch').filter(
            parent=obj,
            child_branch__education_group_type__name=GroupType.COMMON_CORE.name
        ).first()
        if common_core:
            extra_intro_offers.append(common_core.child_branch)
        return extra_intro_offers
