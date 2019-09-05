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
from collections import OrderedDict
from operator import itemgetter

from django.db.models import Prefetch
from django.utils.translation import ugettext_lazy as _

from base import models as mdl_base
from base.business.entity import get_entity_calendar
from base.business.learning_unit_year_with_context import volume_learning_component_year
from base.models import learning_achievement
from base.models.academic_calendar import AcademicCalendar
from base.models.enums import academic_calendar_type
from base.models.enums import entity_container_year_link_type
from base.models.enums.academic_calendar_type import SUMMARY_COURSE_SUBMISSION
from base.models.enums.entity_container_year_link_type import REQUIREMENT_ENTITIES
from base.models.learning_component_year import LearningComponentYear
from base.models.learning_container_year import find_last_entity_version_grouped_by_linktypes
from base.models.utils.utils import get_object_or_none
from cms import models as mdl_cms
from cms.enums import entity_name
from osis_common.utils.datetime import convert_date_to_datetime

CMS_LABEL_SPECIFICATIONS = ['themes_discussed', 'prerequisite']

CMS_LABEL_PEDAGOGY_FR_AND_EN = ['resume', 'teaching_methods', 'evaluation_methods', 'other_informations',
                                'online_resources']
CMS_LABEL_PEDAGOGY_FR_ONLY = ['bibliography', 'mobility']
CMS_LABEL_PEDAGOGY = CMS_LABEL_PEDAGOGY_FR_AND_EN + CMS_LABEL_PEDAGOGY_FR_ONLY

CMS_LABEL_SUMMARY = ['resume']

COLORED = 'COLORED_ROW'


def get_same_container_year_components(learning_unit_year):
    learning_container_year = learning_unit_year.learning_container_year
    components = []

    learning_components_year = LearningComponentYear.objects.filter(
        learning_unit_year__learning_container_year=learning_container_year
    ).prefetch_related(
        Prefetch('learningclassyear_set', to_attr="classes"),
    ).select_related('learning_unit_year').order_by('type', 'acronym')

    additionnal_entities = get_entities(learning_container_year)

    for learning_component_year in learning_components_year:
        if learning_component_year.classes:
            for learning_class_year in learning_component_year.classes:
                learning_class_year.used_by_learning_units_year = learning_unit_year.acronym
                learning_class_year.is_used_by_full_learning_unit_year = _is_used_by_full_learning_unit_year(
                    learning_class_year)

        used_by_learning_unit = learning_component_year.learning_unit_year == learning_unit_year

        components.append(
            {
                'learning_component_year': learning_component_year,
                'volumes': volume_learning_component_year(learning_component_year),
                'learning_unit_usage': _learning_unit_usage(learning_component_year.learning_unit_year),
                'used_by_learning_unit': used_by_learning_unit
            }
        )
    components = sorted(components, key=itemgetter('learning_unit_usage'))
    return compose_components_dict(components, additionnal_entities)


def get_organization_from_learning_unit_year(learning_unit_year):
    if learning_unit_year.campus:
        return learning_unit_year.campus.organization


def get_all_attributions(learning_unit_year):
    attributions = {}
    if learning_unit_year.learning_container_year:
        all_attributions = find_last_entity_version_grouped_by_linktypes(
            learning_unit_year.learning_container_year)

        attributions['requirement_entity'] = all_attributions.get(entity_container_year_link_type.REQUIREMENT_ENTITY)
        attributions['allocation_entity'] = all_attributions.get(entity_container_year_link_type.ALLOCATION_ENTITY)
        attributions['additional_requirement_entity_1'] = \
            all_attributions.get(entity_container_year_link_type.ADDITIONAL_REQUIREMENT_ENTITY_1)
        attributions['additional_requirement_entity_2'] = \
            all_attributions.get(entity_container_year_link_type.ADDITIONAL_REQUIREMENT_ENTITY_2)
    return attributions


def get_cms_label_data(cms_label, user_language):
    cms_label_data = OrderedDict()
    translated_labels = mdl_cms.translated_text_label.search(text_entity=entity_name.LEARNING_UNIT_YEAR,
                                                             labels=cms_label,
                                                             language=user_language)

    for label in cms_label:
        translated_text = next((trans.label for trans in translated_labels if trans.text_label.label == label), None)
        cms_label_data[label] = translated_text

    return cms_label_data


def _learning_unit_usage(learning_unit_year):
    return "{} ({})".format(
        learning_unit_year.acronym,
        _(learning_unit_year.quadrimester) if learning_unit_year.quadrimester else '?'
    )


def get_components_identification(learning_unit_yr):
    components = []
    additional_entities = get_entities(learning_unit_yr.learning_container_year)

    learning_component_year_list_from_luy = LearningComponentYear.objects.filter(
        learning_unit_year=learning_unit_yr
    ).order_by('type', 'acronym')

    for learning_component_year in learning_component_year_list_from_luy:
        components.append(
            {
                'learning_component_year': learning_component_year,
                'volumes': volume_learning_component_year(learning_component_year)
            }
        )

    return compose_components_dict(components, additional_entities)


def _is_used_by_full_learning_unit_year(a_learning_class_year):
    return a_learning_class_year.learning_component_year.learning_unit_year.is_full()


def get_entity_acronym(an_entity):
    return an_entity.acronym if an_entity else None


def is_summary_submission_opened():
    current_academic_year = mdl_base.academic_year.starting_academic_year()
    return mdl_base.academic_calendar. \
        is_academic_calendar_opened_for_specific_academic_year(current_academic_year,
                                                               academic_calendar_type.SUMMARY_COURSE_SUBMISSION)


def compose_components_dict(components, additional_entities):
    data_components = {'components': components}
    data_components.update(additional_entities)
    return data_components


def get_entities(container_year):
    return {
        link_type: entity.most_recent_acronym if entity else None
        for link_type, entity in container_year.get_map_entity_by_type().items()
        if link_type in REQUIREMENT_ENTITIES
    }


def _get_summary_status(a_calendar, cms_list, lu):
    for educational_information in cms_list:
        if educational_information.reference == lu.id \
                and _changed_in_period(a_calendar.start_date, educational_information.changed):
            return True
    return False


def _get_calendar(academic_yr, an_entity_version):
    """ Try to fetch the academic calendar for the entity. If it is not found, return the academic calendar. """
    a_calendar = get_entity_calendar(an_entity_version, academic_yr)  # TODO slow method...
    if a_calendar is None:
        a_calendar = get_object_or_none(
            AcademicCalendar, reference=SUMMARY_COURSE_SUBMISSION, academic_year=academic_yr
        )
    return a_calendar


def _changed_in_period(start_date, changed_date):
    return convert_date_to_datetime(start_date) <= changed_date


def _set_summary_status_on_luy(cms_list, learning_unit_yr):
    requirement_entity = learning_unit_yr.entities.get('REQUIREMENT_ENTITY', None)
    if requirement_entity:
        a_calendar = _get_calendar(learning_unit_yr.academic_year.past(), requirement_entity)
        if a_calendar:
            learning_unit_yr.summary_status = _get_summary_status(a_calendar, cms_list, learning_unit_yr)


def get_achievements_group_by_language(learning_unit_year):
    achievement_grouped = {}
    all_achievements = learning_achievement.find_by_learning_unit_year(learning_unit_year)
    for achievement in all_achievements:
        key = 'achievements_{}'.format(achievement.language.code)
        achievement_grouped.setdefault(key, []).append(achievement)
    return achievement_grouped


def get_learning_unit_comparison_context(learning_unit_year):
    context = dict({'learning_unit_year': learning_unit_year})
    context['campus'] = learning_unit_year.campus
    context['organization'] = get_organization_from_learning_unit_year(learning_unit_year)
    components = get_components_identification(learning_unit_year)
    context['components'] = components.get('components')
    context['learning_container_year_partims'] = learning_unit_year.get_partims_related()
    context.update(learning_unit_year.learning_container_year.get_map_entity_by_type())
    return context
