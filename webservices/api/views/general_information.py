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
from cms.models.translated_text import TranslatedText
from cms.models.translated_text_label import TranslatedTextLabel
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
        common_egy = EducationGroupYear.objects.get_common(
            academic_year=egy.academic_year
        )
        translated_text_labels = TranslatedTextLabel.objects.filter(
            text_label__label=OuterRef('text_label__label'),
            language=self.kwargs['language'],
        ).order_by('label').values('label')[:1]
        common_translated_texts = TranslatedText.objects.filter(
            reference=common_egy.id,
            text_label__label__in=pertinent_sections['common'],
            language=self.kwargs['language']
        )
        translated_texts = TranslatedText.objects.filter(
            reference=egy.id,
            text_label__label__in=pertinent_sections['specific'],
            language=self.kwargs['language']
        )
        translated_texts = translated_texts.annotate(
            translated_label=Subquery(translated_text_labels, output_field=CharField())
        )
        common_translated_texts = common_translated_texts.annotate(
            translated_label=Subquery(translated_text_labels, output_field=CharField())
        )
        for ctt in common_translated_texts:
            egy_queryset = egy_queryset.annotate(**{
                'common_' + ctt.text_label.label: Value(ctt.text, output_field=CharField()) or None,
                'common_' + ctt.text_label.label + '_label': Value(ctt.translated_label, output_field=CharField())
            })
        for ctt in translated_texts:
            egy_queryset = egy_queryset.annotate(**{
                ctt.text_label.label: Value(ctt.text, output_field=CharField()) or None,
                ctt.text_label.label + '_label': Value(ctt.translated_label, output_field=CharField())
            })
        return egy_queryset.first()

    def get_serializer_context(self):
        serializer_context = super().get_serializer_context()
        serializer_context['language'] = self.kwargs['language']
        serializer_context['acronym'] = self.kwargs['acronym']
        return serializer_context
