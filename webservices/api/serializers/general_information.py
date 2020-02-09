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

from django.conf import settings
from rest_framework import serializers

from base.business.education_groups import general_information_sections
from base.business.education_groups.general_information_sections import \
    SKILLS_AND_ACHIEVEMENTS, ADMISSION_CONDITION, CONTACTS, CONTACT_INTRO
from base.models.education_group_year import EducationGroupYear
from webservices.api.serializers.section import SectionSerializer, AchievementSectionSerializer, \
    AdmissionConditionSectionSerializer, ContactsSectionSerializer, EvaluationSectionSerializer
from webservices.business import EVALUATION_KEY

WS_SECTIONS_TO_SKIP = [CONTACT_INTRO]


class GeneralInformationSerializer(serializers.ModelSerializer):
    language = serializers.CharField(read_only=True)
    year = serializers.IntegerField(source='academic_year.year', read_only=True)
    education_group_type = serializers.CharField(source='education_group_type.name', read_only=True)
    education_group_type_text = serializers.CharField(source='education_group_type.get_name_display', read_only=True)
    sections = serializers.SerializerMethodField()

    class Meta:
        model = EducationGroupYear

        fields = (
            'language',
            'acronym',
            'title',
            'year',
            'education_group_type',
            'education_group_type_text',
            'sections',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        lang = kwargs['context']['language']
        acronym = kwargs['context']['acronym'].upper()
        self.instance.language = lang
        if lang != settings.LANGUAGE_CODE_FR[:2]:
            self.fields['title'] = serializers.CharField(source='title_english', read_only=True)
        if self.instance.partial_acronym == acronym:
            self.fields['acronym'] = serializers.CharField(source='partial_acronym', read_only=True)

    def get_sections(self, obj):
        datas = []
        sections = []
        language = settings.LANGUAGE_CODE_FR \
            if self.instance.language == settings.LANGUAGE_CODE_FR[:2] else self.instance.language
        pertinent_sections = general_information_sections.SECTIONS_PER_OFFER_TYPE[obj.education_group_type.name]
        cms_serializers = {
            SKILLS_AND_ACHIEVEMENTS: AchievementSectionSerializer,
            ADMISSION_CONDITION: AdmissionConditionSectionSerializer,
            CONTACTS: ContactsSectionSerializer,
            EVALUATION_KEY: EvaluationSectionSerializer
        }
        if EVALUATION_KEY in pertinent_sections['common']:
            pertinent_sections['common'].remove(EVALUATION_KEY)

        for common_section in pertinent_sections['common']:
            sections.append(_get_section_item(common_section, obj, True))

        for specific_section in pertinent_sections['specific']:
            serializer = cms_serializers.get(specific_section)
            if serializer:
                serializer = serializer(obj) if specific_section == EVALUATION_KEY \
                    else serializer({'id': specific_section}, context={'egy': obj, 'lang': language})
                datas.append(serializer.data)
            elif specific_section not in WS_SECTIONS_TO_SKIP:
                sections.append(_get_section_item(specific_section, obj))
        if self.context.get('intro_offers'):
            sections += [{
                'label': 'intro-' + intro_partial_acronym.lower(),
                'translated_label': getattr(obj, 'intro'),
                'text': getattr(obj, 'intro-' + intro_partial_acronym.lower(), None)
            } for intro_partial_acronym in self.context['intro_offers']]

        datas += SectionSerializer(sections, many=True).data
        return datas


def _get_section_item(section, obj, is_common=False):
    return {
        'label': section + '' if '-commun' in section or not is_common else '-commun',
        'translated_label': getattr(obj, _get_text_prefix_annotation(is_common) + section + '_label'),
        'text': getattr(obj, _get_text_prefix_annotation(is_common) + section, None),
    }


def _get_text_prefix_annotation(is_common=False):
    return 'common_' if is_common else ''
