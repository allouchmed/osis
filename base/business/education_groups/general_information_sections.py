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
from collections import namedtuple

from django.utils.translation import ugettext_lazy as _

# This all text_label which are related to "general information" for education group year
# The key MUST be in french because it depend on Webservice (filtering)
from base.models.enums.education_group_types import TrainingType, MiniTrainingType, GroupType

PEDAGOGY = 'pedagogie'
MOBILITY = 'mobilite'
FURTHER_TRAININGS = 'formations_accessibles'
CERTIFICATES = 'certificats'
COMPLEMENTARY_MODULE = 'module_complementaire'
EVALUATION = 'evaluation'
STRUCTURE = 'structure'
DETAILED_PROGRAM = 'programme_detaille'
WELCOME_INTRODUCTION = 'welcome_introduction'
WELCOME_JOB = 'welcome_job'
WELCOME_PROFIL = 'welcome_profil'
WELCOME_PROGRAM = 'welcome_programme'
WELCOME_PATH = 'welcome_parcours'
CAAP = 'caap'
ACCESS_TO_PROFESSIONS = 'acces_professions'
BACHELOR_CONCERNED = 'bacheliers_concernes'
PRACTICAL_INFO = 'infos_pratiques'
MINORS = 'mineures'
MAJORS = 'majeures'
PURPOSES = 'finalites'
COMMON_DIDACTIC_PURPOSES = 'finalites_didactiques-commun'
AGREGATION = 'agregation'
PREREQUISITE = 'prerequis'
OPTIONS = 'options'
INTRODUCTION = 'intro'
CONTACTS = 'contacts'
CONTACT_INTRO = 'contact_intro'

Section = namedtuple('Section', 'title labels')

SECTION_LIST = [
    Section(title=_('Welcome'),
            labels=[
                WELCOME_INTRODUCTION,
                WELCOME_PROFIL,
                WELCOME_JOB,
                WELCOME_PROGRAM,
                WELCOME_PATH,
                INTRODUCTION,
            ]),
    Section(title=_('Teaching profile'),
            labels=[
                STRUCTURE
            ]),
    Section(title=_('Detailed program'),
            labels=[
                MINORS,
                MAJORS,
                DETAILED_PROGRAM,
                PURPOSES,
                OPTIONS,
                COMMON_DIDACTIC_PURPOSES,
                CAAP,
                AGREGATION,
                PREREQUISITE,
            ]),
    Section(title=_('Admission'),
            labels=[
                ACCESS_TO_PROFESSIONS,
                BACHELOR_CONCERNED,
                COMPLEMENTARY_MODULE
            ]),
    Section(title=_('Benefits and organization'),
            labels=[
                PEDAGOGY,
                EVALUATION,
                MOBILITY,
                FURTHER_TRAININGS,
                CERTIFICATES,
            ]),
    Section(title=_('In practice'),
            labels=[
                PRACTICAL_INFO,
                CONTACT_INTRO,
            ]),
]

# Common type which have admission conditions sections + relevant sections
COMMON_TYPE_ADMISSION_CONDITIONS = {
    TrainingType.BACHELOR.name:
        ('alert_message', 'ca_bacs_cond_generales', 'ca_bacs_cond_particulieres',
         'ca_bacs_examen_langue', 'ca_bacs_cond_speciales', ),
    TrainingType.AGGREGATION.name:
        ('alert_message', 'ca_cond_generales', 'ca_maitrise_fr',
         'ca_allegement', 'ca_ouv_adultes', ),
    TrainingType.PGRM_MASTER_120.name:
        ('alert_message', 'non_university_bachelors', 'adults_taking_up_university_training',
         'personalized_access', 'admission_enrollment_procedures', ),
    TrainingType.MASTER_MC.name: ('alert_message', 'ca_cond_generales', )
}

MIN_YEAR_TO_DISPLAY_GENERAL_INFO_AND_ADMISSION_CONDITION = 2017


SECTIONS_PER_OFFER_TYPE = {
    TrainingType.AGGREGATION.name: {
        'common': [AGREGATION, CAAP, EVALUATION, ],
        'specific': [
            EVALUATION,
            ACCESS_TO_PROFESSIONS,
            PEDAGOGY,
            DETAILED_PROGRAM,
            STRUCTURE,
            WELCOME_INTRODUCTION,
            WELCOME_JOB,
            WELCOME_PROFIL,
            WELCOME_PROGRAM,
            CONTACT_INTRO,
        ]
    },
    TrainingType.CERTIFICATE_OF_PARTICIPATION.name: {
        'common': [],
        'specific': [WELCOME_INTRODUCTION, ]
    },
    TrainingType.CERTIFICATE_OF_SUCCESS.name: {
        'common': [],
        'specific': [WELCOME_INTRODUCTION, ]
    },
    TrainingType.CERTIFICATE_OF_HOLDING_CREDITS.name: {
        'common': [],
        'specific': [WELCOME_INTRODUCTION, ]
    },
    TrainingType.BACHELOR.name: {
        'common': [CAAP, EVALUATION, PREREQUISITE, ],
        'specific': [
            EVALUATION,
            ACCESS_TO_PROFESSIONS,
            CONTACT_INTRO,
            FURTHER_TRAININGS,
            MINORS,
            MOBILITY,
            PEDAGOGY,
            DETAILED_PROGRAM,
            STRUCTURE,
            WELCOME_INTRODUCTION,
            WELCOME_JOB,
            WELCOME_PATH,
            WELCOME_PROFIL,
            WELCOME_PROGRAM,
            PREREQUISITE,
        ]
    },
    TrainingType.CERTIFICATE.name: {
        'common': [CAAP, EVALUATION, PREREQUISITE, ],
        'specific': [
            EVALUATION,
            CONTACT_INTRO,
            MOBILITY,
            PEDAGOGY,
            DETAILED_PROGRAM,
            STRUCTURE,
            WELCOME_INTRODUCTION,
            WELCOME_PATH,
            WELCOME_PROFIL,
            WELCOME_PROGRAM,
            PREREQUISITE,
        ]
    },
    TrainingType.CAPAES.name: {
        'common': [],
        'specific': [WELCOME_INTRODUCTION, ]
    },
    TrainingType.RESEARCH_CERTIFICATE.name: {
        'common': [CAAP, EVALUATION, PREREQUISITE, ],
        'specific': [WELCOME_INTRODUCTION, EVALUATION, PEDAGOGY, DETAILED_PROGRAM, STRUCTURE, ]
    },
    TrainingType.UNIVERSITY_FIRST_CYCLE_CERTIFICATE.name: {
        'common': [],
        'specific': [WELCOME_INTRODUCTION, ]
    },
    TrainingType.UNIVERSITY_SECOND_CYCLE_CERTIFICATE.name: {
        'common': [],
        'specific': [WELCOME_INTRODUCTION, ]
    },
    TrainingType.PGRM_MASTER_120.name: {
        'common': [CAAP, EVALUATION, COMPLEMENTARY_MODULE, PREREQUISITE, ],
        'specific': [
            EVALUATION,
            COMPLEMENTARY_MODULE,
            PREREQUISITE,
            ACCESS_TO_PROFESSIONS,
            CERTIFICATES,
            CONTACT_INTRO,
            PURPOSES,
            FURTHER_TRAININGS,
            MOBILITY,
            OPTIONS,
            PEDAGOGY,
            STRUCTURE,
            WELCOME_INTRODUCTION,
            WELCOME_JOB,
            WELCOME_PATH,
            WELCOME_PROFIL,
            WELCOME_PROGRAM
        ]
    },
    TrainingType.MASTER_MA_120.name: {
        'common': [],
        'specific': [INTRODUCTION, ]
    },
    TrainingType.MASTER_MD_120.name: {
        'common': [COMMON_DIDACTIC_PURPOSES, ],
        'specific': [INTRODUCTION, ]
    },
    TrainingType.MASTER_MS_120.name: {
        'common': [],
        'specific': [INTRODUCTION, ]
    },
    TrainingType.PGRM_MASTER_180_240.name: {
        'common': [CAAP, EVALUATION, COMPLEMENTARY_MODULE, PREREQUISITE, ],
        'specific': [
            EVALUATION,
            ACCESS_TO_PROFESSIONS,
            CERTIFICATES,
            FURTHER_TRAININGS,
            MOBILITY,
            PEDAGOGY,
            STRUCTURE,
            WELCOME_INTRODUCTION,
            WELCOME_JOB,
            WELCOME_PROFIL,
            WELCOME_PROGRAM,
            WELCOME_PATH,
            PURPOSES,
            OPTIONS,
            PREREQUISITE,
            COMPLEMENTARY_MODULE,
            CONTACT_INTRO
        ]
    },
    TrainingType.MASTER_MA_180_240.name: {
        'common': [],
        'specific': [INTRODUCTION, ]
    },
    TrainingType.MASTER_MD_180_240.name: {
        'common': [COMMON_DIDACTIC_PURPOSES, ],
        'specific': [INTRODUCTION, ]
    },
    TrainingType.MASTER_MS_180_240.name: {
        'common': [],
        'specific': [INTRODUCTION, ]
    },
    TrainingType.MASTER_M1.name: {
        'common': [CAAP, EVALUATION, COMPLEMENTARY_MODULE, ],
        'specific': [
            EVALUATION,
            ACCESS_TO_PROFESSIONS,
            CERTIFICATES,
            CONTACT_INTRO,
            FURTHER_TRAININGS,
            MOBILITY,
            OPTIONS,
            PEDAGOGY,
            STRUCTURE,
            WELCOME_INTRODUCTION,
            WELCOME_JOB,
            WELCOME_PATH,
            WELCOME_PROFIL,
            WELCOME_PROGRAM,
            COMPLEMENTARY_MODULE,
        ]
    },
    TrainingType.MASTER_MC.name: {
        'common': [CAAP, EVALUATION, ],
        'specific': [
            EVALUATION,
            ACCESS_TO_PROFESSIONS,
            CONTACT_INTRO,
            FURTHER_TRAININGS,
            MOBILITY,
            PEDAGOGY,
            STRUCTURE,
            WELCOME_INTRODUCTION,
            WELCOME_JOB,
            WELCOME_PATH,
            WELCOME_PROFIL,
            WELCOME_PROGRAM,
            PREREQUISITE
        ]
    },

    MiniTrainingType.DEEPENING.name: {
        'common': [EVALUATION, ],
        'specific': [
            EVALUATION,
            BACHELOR_CONCERNED,
            ACCESS_TO_PROFESSIONS,
            CONTACT_INTRO,
            FURTHER_TRAININGS,
            PRACTICAL_INFO,
            PEDAGOGY,
            DETAILED_PROGRAM,
            STRUCTURE,
            WELCOME_INTRODUCTION,
            WELCOME_PATH,
            WELCOME_PROFIL,
            WELCOME_PROGRAM,
        ]
    },
    MiniTrainingType.SOCIETY_MINOR.name: {
        'common': [EVALUATION, ],
        'specific': [
            EVALUATION,
            BACHELOR_CONCERNED,
            ACCESS_TO_PROFESSIONS,
            CONTACT_INTRO,
            FURTHER_TRAININGS,
            PRACTICAL_INFO,
            PEDAGOGY,
            DETAILED_PROGRAM,
            STRUCTURE,
            WELCOME_INTRODUCTION,
            WELCOME_PATH,
            WELCOME_PROFIL,
            WELCOME_PROGRAM,
        ]
    },
    MiniTrainingType.ACCESS_MINOR.name: {
        'common': [EVALUATION, ],
        'specific': [
            EVALUATION,
            BACHELOR_CONCERNED,
            ACCESS_TO_PROFESSIONS,
            CONTACT_INTRO,
            FURTHER_TRAININGS,
            PRACTICAL_INFO,
            PEDAGOGY,
            DETAILED_PROGRAM,
            STRUCTURE,
            WELCOME_INTRODUCTION,
            WELCOME_PATH,
            WELCOME_PROFIL,
            WELCOME_PROGRAM,
        ]
    },
    MiniTrainingType.OPEN_MINOR.name: {
        'common': [EVALUATION, ],
        'specific': [
            EVALUATION,
            BACHELOR_CONCERNED,
            ACCESS_TO_PROFESSIONS,
            CONTACT_INTRO,
            FURTHER_TRAININGS,
            PRACTICAL_INFO,
            PEDAGOGY,
            DETAILED_PROGRAM,
            STRUCTURE,
            WELCOME_INTRODUCTION,
            WELCOME_PATH,
            WELCOME_PROFIL,
            WELCOME_PROGRAM,
        ]
    },
    MiniTrainingType.DISCIPLINARY_COMPLEMENT_MINOR.name: {
        'common': [EVALUATION, ],
        'specific': [
            EVALUATION,
            BACHELOR_CONCERNED,
            ACCESS_TO_PROFESSIONS,
            CONTACT_INTRO,
            FURTHER_TRAININGS,
            PRACTICAL_INFO,
            PEDAGOGY,
            DETAILED_PROGRAM,
            STRUCTURE,
            WELCOME_INTRODUCTION,
            WELCOME_PATH,
            WELCOME_PROFIL,
            WELCOME_PROGRAM,
        ]
    },
    MiniTrainingType.FSA_SPECIALITY.name: {
        'common': [EVALUATION, ],
        'specific': [
            EVALUATION,
            BACHELOR_CONCERNED,
            ACCESS_TO_PROFESSIONS,
            CONTACT_INTRO,
            FURTHER_TRAININGS,
            PRACTICAL_INFO,
            PEDAGOGY,
            DETAILED_PROGRAM,
            STRUCTURE,
            INTRODUCTION,
            WELCOME_PATH,
            WELCOME_PROFIL,
            WELCOME_PROGRAM,
        ]
    },
    MiniTrainingType.OPTION.name: {
        'common': [],
        'specific': [INTRODUCTION, ]
    },
    MiniTrainingType.MOBILITY_PARTNERSHIP.name: {
        'common': [],
        'specific': []
    },

    GroupType.COMMON_CORE.name: {
        'common': [],
        'specific': [INTRODUCTION, ]
    },

    'common': {
        'common': [],
        'specific': [AGREGATION, CAAP, PREREQUISITE, COMMON_DIDACTIC_PURPOSES, COMPLEMENTARY_MODULE, EVALUATION, ]
    }
}
