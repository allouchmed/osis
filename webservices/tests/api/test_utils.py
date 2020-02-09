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
from django.db.models import Value, CharField

from base.models.education_group_year import EducationGroupYear
from cms.enums.entity_name import OFFER_YEAR
from cms.tests.factories.translated_text import TranslatedTextFactory
from cms.tests.factories.translated_text_label import TranslatedTextLabelFactory
from webservices.business import SKILLS_AND_ACHIEVEMENTS_INTRO, SKILLS_AND_ACHIEVEMENTS_EXTRA


def get_annotated_egy_qs(egy, annotations):
    annotated_egy_qs = EducationGroupYear.objects.filter(id=egy.id)
    for label, (translated_label, text) in annotations.items():
        annotated_egy_qs = annotated_egy_qs.annotate(**{
            label + '_label': Value(translated_label, output_field=CharField()),
            label: Value(text or None, output_field=CharField())
        })
    return annotated_egy_qs


def create_cms_texts(language, egy, annotations, pertinent_sections):
    for section in pertinent_sections:
        t_label = TranslatedTextLabelFactory(language=language, text_label__label=section)
        t = TranslatedTextFactory(
            reference=egy.id,
            entity=OFFER_YEAR,
            language=language,
            text_label__label=section
        )
        annotations.update({section: (t_label.label, t.text)})
    _create_cms_achievements(egy, language)
    return annotations


def _create_cms_achievements(egy, language):
    for label in [SKILLS_AND_ACHIEVEMENTS_INTRO, SKILLS_AND_ACHIEVEMENTS_EXTRA]:
        TranslatedTextFactory(
            text_label__label=label,
            reference=egy.id,
            entity=OFFER_YEAR,
            language=language
        )
