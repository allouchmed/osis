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
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _, pgettext

from base.business.event_perms import EventPermEducationGroupEdition
from base.models import program_manager
from base.models.education_group import EducationGroup
from base.models.education_group_type import EducationGroupType
from base.models.education_group_year import EducationGroupYear
from base.models.enums.education_group_categories import TRAINING, MINI_TRAINING, Categories
from base.models.program_manager import is_program_manager
from program_management.business.group_element_years import postponement, management

ERRORS_MSG = {
    "base.add_educationgroup": _("The user has not permission to create education groups."),
    "base.change_educationgroup": _("The user has not permission to change education groups."),
    "base.delete_educationgroup": _("The user has not permission to delete education groups."),
    "base.change_educationgroupcontent": _("The user is not allowed to change education group content.")
}


def is_eligible_to_add_training(person, education_group_yr, raise_exception=False):
    return _is_eligible_to_add_education_group(
        person, education_group_yr, Categories.TRAINING, raise_exception=raise_exception
    )


def is_eligible_to_add_mini_training(person, education_group_yr, raise_exception=False):
    return _is_eligible_to_add_education_group(
        person, education_group_yr, Categories.MINI_TRAINING, raise_exception=raise_exception
    )


def is_eligible_to_add_group(person, education_group_yr, raise_exception=False):
    return _is_eligible_to_add_education_group(
        person, education_group_yr, Categories.GROUP, raise_exception=raise_exception
    )


def _is_eligible_to_add_education_group(person, education_group_yr, category, education_group_type=None,
                                        raise_exception=False):
    return check_permission(person, "base.add_educationgroup", raise_exception) and \
           _is_eligible_to_add_education_group_with_category(person, education_group_yr, category, raise_exception) and\
           _is_eligible_education_group(person, education_group_yr, raise_exception) and \
           (not management.is_max_child_reached(education_group_yr, education_group_type.name)
            if education_group_type and education_group_yr
            else check_authorized_type(education_group_yr, category, raise_exception))


def is_eligible_to_change_education_group(person, education_group_yr, raise_exception=False):
    return check_permission(person, "base.change_educationgroup", raise_exception) and \
           _is_eligible_education_group(person, education_group_yr, raise_exception) and \
           _is_year_editable(education_group_yr, raise_exception) and \
           _is_eligible_education_group_category(person, education_group_yr, raise_exception)


def is_eligible_to_change_education_group_content(person, education_group_yr, raise_exception=False):
    return check_permission(person, "base.change_educationgroupcontent", raise_exception) and \
        is_eligible_to_change_education_group(person, education_group_yr, raise_exception)


def _is_year_editable(education_group_yr, raise_exception):
    error_msg = None
    if education_group_yr.academic_year.year < settings.YEAR_LIMIT_EDG_MODIFICATION:
        error_msg = _("You cannot change a education group before %(limit_year)s") % {
            "limit_year": settings.YEAR_LIMIT_EDG_MODIFICATION}

    result = error_msg is None
    can_raise_exception(raise_exception, result, error_msg)
    return result


def is_eligible_to_change_coorganization(person, education_group_yr, raise_exception=False):
    return check_permission(person, "base.change_educationgroup", raise_exception) and \
           check_link_to_management_entity(education_group_yr, person, raise_exception) and person.is_central_manager


def is_eligible_to_postpone_education_group(person, education_group_yr, raise_exception=False):
    result = check_permission(person, "base.change_educationgroup", raise_exception) and \
             _is_eligible_education_group(person, education_group_yr, raise_exception)

    try:
        # Check if the education group is valid
        postponement.PostponeContent(education_group_yr.previous_year(), person)
    except postponement.NotPostponeError as e:
        result = False
        if raise_exception:
            raise PermissionDenied(str(e))
    return result


def is_eligible_to_add_achievement(person, education_group_yr, raise_exception=False):
    return check_permission(person, "base.add_educationgroupachievement", raise_exception) and \
           check_link_to_management_entity(education_group_yr, person, raise_exception)


def is_eligible_to_change_achievement(person, education_group_yr, raise_exception=False):
    return check_permission(person, "base.change_educationgroupachievement", raise_exception) and \
           check_link_to_management_entity(education_group_yr, person, raise_exception)


def is_eligible_to_delete_achievement(person, education_group_yr, raise_exception=False):
    return check_permission(person, "base.delete_educationgroupachievement", raise_exception) and \
           check_link_to_management_entity(education_group_yr, person, raise_exception)


def is_eligible_to_delete_education_group(person, education_group_yr, raise_exception=False):
    return check_permission(person, "base.delete_educationgroup", raise_exception) and \
           _is_eligible_education_group(person, education_group_yr, raise_exception) and \
           person.is_central_manager or \
           (person.is_faculty_manager and _is_edition_period_open(education_group_yr, raise_exception))


def is_eligible_to_delete_education_group_year(person, education_group_yr, raise_exception=False):
    return can_delete_all_education_group(person.user, education_group_yr.education_group)


def _is_eligible_education_group(person, education_group_yr, raise_exception):
    return (
        is_eligible_education_group_program_manager(education_group_yr, person) or
        check_link_to_management_entity(education_group_yr, person, raise_exception) and
        (
            person.is_central_manager or person.is_faculty_manager or
            _is_edition_period_open(education_group_yr, raise_exception)
        )
    )


def is_eligible_education_group_program_manager(education_group_yr, person):
    is_pgm_manager_only = person.is_program_manager and not(person.is_faculty_manager or person.is_central_manager)
    return _is_education_group_program_manager(person, education_group_yr, raise_exception=is_pgm_manager_only)


def _is_eligible_education_group_category(person, education_group_yr, raise_exception):
    result = (education_group_yr.education_group_type.category in [TRAINING, MINI_TRAINING] or
              person.is_faculty_manager and _is_edition_period_open(education_group_yr, False) or
              person.is_central_manager)
    error_msg = _('The user can only edit a training or a mini-training during this period')
    can_raise_exception(raise_exception, result, error_msg)
    return result


def _is_education_group_program_manager(person, education_group_yr, raise_exception):
    result = education_group_yr and is_program_manager(person.user, education_group=education_group_yr.education_group)
    error_msg = _('The user is not the program manager of the education group')
    can_raise_exception(person.is_program_manager and raise_exception, result, error_msg)
    return result


def _is_edition_period_open(education_group_yr, raise_exception):
    return EventPermEducationGroupEdition(obj=education_group_yr, raise_exception=raise_exception).is_open()


def _is_eligible_to_add_education_group_with_category(person, education_group_yr, category, raise_exception):
    # TRAINING/MINI_TRAINING can only be added by central managers | Faculty manager must make a proposition of creation
    # based on US OSIS-2592, Faculty manager can add a MINI-TRAINING
    result = person.is_central_manager or (
            person.is_faculty_manager and (category == Categories.MINI_TRAINING or
                                           (category == Categories.GROUP and education_group_yr is not None))
    )

    msg = pgettext(
        "male" if category == Categories.GROUP else "female",
        "The user has not permission to create a %(category)s."
    ) % {"category": category.value}

    can_raise_exception(raise_exception, result, msg)

    return result


def check_link_to_management_entity(education_group_yr, person, raise_exception):
    if education_group_yr:
        if not hasattr(education_group_yr, 'eligible_entities'):
            education_group_yr.eligible_entities = get_education_group_year_eligible_management_entities(
                education_group_yr
            )
        result = person.is_attached_entities(education_group_yr.eligible_entities)
    else:
        result = True

    can_raise_exception(raise_exception, result, _("The user is not attached to the management entity"))

    return result


def check_permission(person, permission, raise_exception=False):
    result = person.user.has_perm(permission)
    can_raise_exception(raise_exception, result, ERRORS_MSG.get(permission, ""))
    return result


def can_raise_exception(raise_exception, result, msg):
    if raise_exception and not result:
        raise PermissionDenied(_(msg).capitalize())


def check_authorized_type(education_group_yr: EducationGroupYear, category, raise_exception=False):
    if not education_group_yr or not category:
        return True

    result = EducationGroupType.objects.filter(
        category=category.name,
        authorized_child_type__parent_type__educationgroupyear=education_group_yr
    ).exists()

    parent_category = education_group_yr.education_group_type.category

    can_raise_exception(
        raise_exception, result,
        pgettext(
            "female" if parent_category in [TRAINING, MINI_TRAINING] else "male",
            "No type of %(child_category)s can be created as child of %(category)s of type %(type)s")
        % {
            "child_category": category.value,
            "category": education_group_yr.education_group_type.get_category_display(),
            "type": education_group_yr.education_group_type.get_name_display(),
        }
    )

    return result


def get_education_group_year_eligible_management_entities(education_group_yr: EducationGroupYear):
    if education_group_yr and education_group_yr.management_entity:
        return [education_group_yr.management_entity]

    eligible_entities = []
    for group in education_group_yr.child_branch.all().select_related('parent'):
        eligible_entities += get_education_group_year_eligible_management_entities(group.parent)

    return eligible_entities


def is_eligible_to_edit_general_information(person, education_group_year, raise_exception=False):
    perm = GeneralInformationPerms(person.user, education_group_year)
    return perm.is_eligible(raise_exception)


def is_eligible_to_edit_admission_condition(person, education_group_year, raise_exception=False):
    perm = AdmissionConditionPerms(person.user, education_group_year)
    return perm.is_eligible(raise_exception)


class CommonEducationGroupStrategyPerms(object):
    def __init__(self, user, education_group_year):
        self.user = user
        self.education_group_year = education_group_year
        super().__init__()

    @cached_property
    def person(self):
        return self.user.person

    def is_eligible(self, raise_exception=False):
        try:
            return self._is_eligible()
        except PermissionDenied:
            if not raise_exception:
                return False
            raise

    def _is_eligible(self):
        if self._is_lower_than_limit_edg_year():
            raise PermissionDenied(_("You cannot change a education group before %(limit_year)s") % {
                "limit_year": settings.YEAR_LIMIT_EDG_MODIFICATION
            })
        if self.user.is_superuser:
            return True
        if not self._is_linked_to_management_entity():
            raise PermissionDenied(_("The user is not attached to the management entity"))
        return True

    def _is_lower_than_limit_edg_year(self):
        return self.education_group_year.academic_year.year < settings.YEAR_LIMIT_EDG_MODIFICATION

    def _is_linked_to_management_entity(self):
        return check_link_to_management_entity(self.education_group_year, self.person, False)


class GeneralInformationPerms(CommonEducationGroupStrategyPerms):
    def _is_eligible(self):
        super()._is_eligible()

        if not self._is_user_have_perm():
            raise PermissionDenied(_("The user doesn't have right to update general information"))
        if self.person.is_central_manager:
            return self._is_central_manager_eligible()
        elif self.person.is_faculty_manager:
            return self._is_faculty_manager_eligible()
        elif self.person.is_sic:
            return self._is_sic_eligible()
        return False

    def _is_user_have_perm(self):
        perm_name = 'base.change_commonpedagogyinformation' if self.education_group_year.is_common else \
            'base.change_pedagogyinformation'
        return check_permission(self.person, perm_name, False)

    def _is_central_manager_eligible(self):
        return True

    def _is_faculty_manager_eligible(self):
        return True

    def _is_sic_eligible(self):
        return True


class AdmissionConditionPerms(CommonEducationGroupStrategyPerms):
    def _is_eligible(self):
        super()._is_eligible()

        if not self._is_user_have_perm():
            raise PermissionDenied(_("The user doesn't have right to update admission condition"))

        if self.person.is_central_manager:
            return self._is_central_manager_eligible()
        elif self.person.is_faculty_manager:
            return self._is_faculty_manager_eligible()
        elif self.person.is_sic:
            return self._is_sic_eligible()
        return False

    def _is_user_have_perm(self):
        perm_name = 'base.change_commonadmissioncondition' if self.education_group_year.is_common else \
            'base.change_admissioncondition'
        return check_permission(self.person, perm_name, False)

    def _is_central_manager_eligible(self):
        return True

    def _is_faculty_manager_eligible(self):
        if not EventPermEducationGroupEdition(obj=self.education_group_year, raise_exception=False).is_open():
            raise PermissionDenied(_("The faculty manager cannot modify outside of program edition period"))
        return True

    def _is_sic_eligible(self):
        return True


def can_delete_all_education_group(user, education_group: EducationGroup):
    for education_group_yr in education_group.educationgroupyear_set.all():
        if not is_eligible_to_delete_education_group(user.person, education_group_yr, raise_exception=True):
            raise PermissionDenied
    return True


class CertificateAimsPerms(CommonEducationGroupStrategyPerms):
    """
    Certification aims can only be modified by program manager no matter the program edition period
    """
    def _is_eligible(self):
        if self.education_group_year.education_group_type.category != TRAINING:
            raise PermissionDenied(_("The education group is not a training type"))
        if self.education_group_year.academic_year.year < settings.YEAR_LIMIT_EDG_MODIFICATION:
            raise PermissionDenied(_("You cannot change a education group before %(limit_year)s") % {
                "limit_year": settings.YEAR_LIMIT_EDG_MODIFICATION
            })

        if self.user.is_superuser:
            return True
        if not program_manager.is_program_manager(self.user, education_group=self.education_group_year.education_group):
            raise PermissionDenied(_("The user is not the program manager of the education group"))
        return True
