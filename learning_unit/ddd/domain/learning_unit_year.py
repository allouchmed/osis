##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2020 Université catholique de Louvain (http://www.uclouvain.be)
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
from _decimal import Decimal
from typing import List, Set, Dict

from base.models.enums.education_group_types import EducationGroupTypesEnum, TrainingType
from base.models.enums.learning_unit_year_periodicity import PeriodicityEnum
from base.models.enums.link_type import LinkTypes
from base.models.enums.proposal_type import ProposalType
from program_management.ddd.business_types import *
from program_management.ddd.domain.link import factory as link_factory
from program_management.ddd.domain.prerequisite import Prerequisite
from program_management.models.enums.node_type import NodeType


class LearningUnitYear:
    def __init__(
            self,
            id: int = None,
            year: int = None,
            acronym: str = None,
            common_title_fr: str = '',
            specific_title_fr: str = '',
            common_title_en: str = '',
            specific_title_en: str = '',
            start_year: int = None,
            end_year: int = None,
            proposal_type: ProposalType = None,
            credits: Decimal = None,
            status: bool = None,
            periodicity: PeriodicityEnum = None
    ):
        self.id = id
        self.year = year
        self.acronym = acronym
        self.common_title_fr = common_title_fr or ''
        self.specific_title_fr = specific_title_fr or ''
        self.common_title_en = common_title_en or ''
        self.specific_title_en = specific_title_en or ''
        self.start_date = start_year
        self.end_date = end_year
        self.proposal_type = proposal_type
        self.credits = credits
        self.status = status
        self.periodicity = periodicity

    @property
    def full_title_fr(self):
        return self.common_title_fr + self.specific_title_fr

    @property
    def full_title_en(self):
        return self.common_title_en + self.specific_title_en