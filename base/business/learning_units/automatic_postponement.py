# ##################################################################################################
#  OSIS stands for Open Student Information System. It's an application                            #
#  designed to manage the core business of higher education institutions,                          #
#  such as universities, faculties, institutes and professional schools.                           #
#  The core business involves the administration of students, teachers,                            #
#  courses, programs and so on.                                                                    #
#                                                                                                  #
#  Copyright (C) 2015-2019 Université catholique de Louvain (http://www.uclouvain.be)              #
#                                                                                                  #
#  This program is free software: you can redistribute it and/or modify                            #
#  it under the terms of the GNU General Public License as published by                            #
#  the Free Software Foundation, either version 3 of the License, or                               #
#  (at your option) any later version.                                                             #
#                                                                                                  #
#  This program is distributed in the hope that it will be useful,                                 #
#  but WITHOUT ANY WARRANTY; without even the implied warranty of                                  #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                                   #
#  GNU General Public License for more details.                                                    #
#                                                                                                  #
#  A copy of this license - GNU General Public License - is available                              #
#  at the root of the source code of this program.  If not,                                        #
#  see http://www.gnu.org/licenses/.                                                               #
# ##################################################################################################
from django.db.models import Q
from django.utils.translation import ugettext as _

from base.business.learning_units.edition import duplicate_learning_unit_year
from base.business.utils.postponement import AutomaticPostponementToN6
from base.models.learning_unit import LearningUnit
from base.utils.send_mail import send_mail_before_annual_procedure_of_automatic_postponement_of_luy, \
    send_mail_after_annual_procedure_of_automatic_postponement_of_luy


class LearningUnitAutomaticPostponementToN6(AutomaticPostponementToN6):
    model = LearningUnit
    annualized_set = "learningunityear"

    send_before = send_mail_before_annual_procedure_of_automatic_postponement_of_luy
    send_after = send_mail_after_annual_procedure_of_automatic_postponement_of_luy
    extend_method = duplicate_learning_unit_year
    msg_result = _("%(number_extended)s learning unit(s) extended and %(number_error)s error(s)")

    def get_queryset(self, queryset=None):
        return super().get_queryset(queryset).filter(
            # Ignoring classes - FIXME :: remove this when classes are in separate Model
            learningunityear__learning_container_year__isnull=False
        ).filter(
            # Ignoring external learning units of "mobility" (too much dirty data - to clean into EPC)
            Q(learningunityear__externallearningunityear__mobility=False)
            | Q(learningunityear__externallearningunityear__isnull=True)
        ).distinct()
