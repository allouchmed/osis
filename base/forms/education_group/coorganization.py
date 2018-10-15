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
from django import forms
from django.forms import ModelChoiceField
from django.utils.translation import ugettext_lazy as _

from base.models.education_group_organization import EducationGroupOrganization
from base.models.education_group_year import EducationGroupYear
from reference.models.country import Country
from base.models.organization import Organization, find_by_id
from base.models.entity import Entity


class CoorganizationEditForm(forms.ModelForm):
    country = ModelChoiceField(
        queryset=Country.objects.filter(entity__isnull=False).distinct().order_by('name'),
        required=True,
        label=_("country")
    )

    organization = ModelChoiceField(
        queryset=Organization.objects.none(),
        required=True,
        label=_("institution")
    )

    class Meta:
        model = EducationGroupOrganization
        fields = ['country', 'organization',
                  'all_students', 'enrollment_place', 'diploma', 'is_producing_cerfificate', 'is_producing_annexe']

    def __init__(self, data=None, initial=None, **kwargs):

        super().__init__(data, initial=initial, **kwargs)
        if data:
            self.fields['organization'].queryset = Organization.objects \
                .filter(pk=data['organization'])

            self.organization = find_by_id(data['organization'])
        else:
            if self.instance and self.instance.pk:
                country_id = None
                if self.instance.organization:

                    entity = self.instance.organization.latest_version.entity
                    self.fields['country'].initial = entity.country
                    if entity.country:
                        country_id = entity.country.id

                if self.instance.organization:
                    self.set_organization_data(self.instance.organization.id, country_id)

    def clean_all_students(self):
        data_cleaned = self.cleaned_data.get('all_students')
        if data_cleaned:
            return data_cleaned
        return False

    def clean_enrollment_place(self):
        data_cleaned = self.cleaned_data.get('enrollment_place')
        if data_cleaned:
            return data_cleaned
        return False

    def clean_is_producing_cerfificate(self):
        data_cleaned = self.cleaned_data.get('is_producing_cerfificate')
        if data_cleaned:
            return data_cleaned
        return False

    def clean_is_producing_annexe(self):
        data_cleaned = self.cleaned_data.get('is_producing_annexe')
        if data_cleaned:
            return data_cleaned
        return False

    def set_organization_data(self, organization_id, country_id):
        if country_id:
            organizations = Entity.objects.filter(country__pk=country_id).distinct('organization')
            list_orgs = []

            for i in organizations:
                list_orgs.append(i.organization.id)
            self.fields['organization'].queryset = Organization.objects.filter(id__in=list_orgs)
        else:
            self.fields['organization'].queryset = Organization.objects \
                .filter(pk=organization_id)
        self.fields['organization'].initial = find_by_id(organization_id)
        self.organization = find_by_id(organization_id)

    def save_coorganization(self, education_group_year_id, *args, **kwargs):
        self.instance.education_group_year = EducationGroupYear.objects.get(pk=education_group_year_id)
        return self.save(*args, **kwargs)
