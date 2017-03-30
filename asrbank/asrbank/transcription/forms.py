"""
Definition of forms.
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import ugettext_lazy as _

from asrbank.transcription.models import *


def init_choices(obj, sFieldName, sSet):
    if (obj.fields != None and sFieldName in obj.fields):
        obj.fields[sFieldName].choices = build_choice_list(sSet)
        obj.fields[sFieldName].help_text = get_help(sSet)


class BootstrapAuthenticationForm(AuthenticationForm):
    """Authentication form which uses boostrap CSS."""
    username = forms.CharField(max_length=254,
                               widget=forms.TextInput({
                                   'class': 'form-control',
                                   'placeholder': 'User name'}))
    password = forms.CharField(label=_("Password"),
                               widget=forms.PasswordInput({
                                   'class': 'form-control',
                                   'placeholder':'Password'}))


class LanguageAdminForm(forms.ModelForm):

    class Meta:
        model = Language
        fields = '__all__'
        widgets = { 'name': forms.Select(attrs={'width': 30}) }

    def __init__(self, *args, **kwargs):
        super(LanguageAdminForm, self).__init__(*args, **kwargs)
        init_choices(self, 'name', INTERVIEW_LANGUAGE)


class FileFormatAdminForm(forms.ModelForm):

    class Meta:
        model = FileFormat
        fields = '__all__'
        widgets = { 'name': forms.Select(attrs={'width': 30}) }

    def __init__(self, *args, **kwargs):
        super(FileFormatAdminForm, self).__init__(*args, **kwargs)
        init_choices(self, 'name', AUDIOVIDEO_FORMAT)


class AvailabilityAdminForm(forms.ModelForm):

    class Meta:
        model = Availability
        fields = '__all__'
        widgets = { 'name': forms.Select(attrs={'width': 30}) }

    def __init__(self, *args, **kwargs):
        super(AvailabilityAdminForm, self).__init__(*args, **kwargs)
        init_choices(self, 'name', AVAILABILITY)


class IntervieweeAdminForm(forms.ModelForm):

    class Meta:
        model = Interviewee
        fields = '__all__'
        widgets = {'code': forms.Textarea(attrs={'rows': 1, 'cols': 20}),
                   'name': forms.Textarea(attrs={'rows': 1, 'cols': 80}),
                   'gender': forms.Select(attrs={'width': 30}),
                   'age': forms.Textarea(attrs={'rows': 1, 'cols': 5})  }

    def __init__(self, *args, **kwargs):
        super(IntervieweeAdminForm, self).__init__(*args, **kwargs)
        init_choices(self, 'gender', PARTICIPANT_GENDER)


class InterviewerAdminForm(forms.ModelForm):

    class Meta:
        model = Interviewer
        fields = '__all__'
        widgets = {'code': forms.Textarea(attrs={'rows': 1, 'cols': 20}),
                   'name': forms.Textarea(attrs={'rows': 1, 'cols': 80}),
                   'gender': forms.Select(attrs={'width': 30}),
                   'age': forms.Textarea(attrs={'rows': 1, 'cols': 5})  }

    def __init__(self, *args, **kwargs):
        super(InterviewerAdminForm, self).__init__(*args, **kwargs)
        init_choices(self, 'gender', PARTICIPANT_GENDER)


class TemporalCoverageAdminForm(forms.ModelForm):

    class Meta:
        model = TemporalCoverage
        fields = '__all__'
        widgets = {'startYear': forms.Textarea(attrs={'rows': 1, 'cols': 20}),
                   'endYear': forms.Textarea(attrs={'rows': 1, 'cols': 20})}


class SpatialCoverageAdminForm(forms.ModelForm):

    class Meta:
        model = SpatialCoverage
        fields = '__all__'
        widgets = {'country': forms.Select(attrs={'width': 30}),
                   'place': forms.Textarea(attrs={'rows': 1, 'cols': 80})  }

    def __init__(self, *args, **kwargs):
        super(SpatialCoverageAdminForm, self).__init__(*args, **kwargs)
        init_choices(self, 'country', COVERAGE_SPATIAL_COUNTRY)


class GenreAdminForm(forms.ModelForm):

    class Meta:
        model = Genre
        fields = '__all__'
        widgets = { 'name': forms.Select(attrs={'width': 30}) }

    def __init__(self, *args, **kwargs):
        super(GenreAdminForm, self).__init__(*args, **kwargs)
        init_choices(self, 'name', INTERVIEW_GENRE)


class AnnotationAdminForm(forms.ModelForm):

    class Meta:
        model = Annotation
        fields = '__all__'
        widgets = { 'type':   forms.Select(attrs={'width': 30}),
                    'mode':   forms.Select(attrs={'width': 30}),
                    'format': forms.Select(attrs={'width': 30}) }

    def __init__(self, *args, **kwargs):
        super(AnnotationAdminForm, self).__init__(*args, **kwargs)
        init_choices(self, 'type', ANNOTATION_TYPE)
        init_choices(self, 'mode', ANNOTATION_MODE)
        init_choices(self, 'format', ANNOTATION_FORMAT)


class AnonymisationAdminForm(forms.ModelForm):

    class Meta:
        model = Anonymisation
        fields = '__all__'
        widgets = { 'name': forms.Select(attrs={'width': 30}) }

    def __init__(self, *args, **kwargs):
        super(AnonymisationAdminForm, self).__init__(*args, **kwargs)
        init_choices(self, 'name', ANONYMISATION)


