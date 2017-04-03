"""
Definition of forms.
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
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
    

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    last_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', )


class LanguageAdminForm(forms.ModelForm):

    class Meta:
        model = Language
        fields = ['name']
        widgets = { 'name': forms.Select(attrs={'width': 30}) }

    def __init__(self, *args, **kwargs):
        super(LanguageAdminForm, self).__init__(*args, **kwargs)
        init_choices(self, 'name', INTERVIEW_LANGUAGE)
        self.fields['name'].initial = choice_value("interview.language", "Dutch (Northern)")


class FileFormatAdminForm(forms.ModelForm):

    class Meta:
        model = FileFormat
        fields = ['name']
        widgets = { 'name': forms.Select(attrs={'width': 30}) }

    def __init__(self, *args, **kwargs):
        super(FileFormatAdminForm, self).__init__(*args, **kwargs)
        init_choices(self, 'name', AUDIOVIDEO_FORMAT)


class AvailabilityAdminForm(forms.ModelForm):

    class Meta:
        model = Availability
        fields = ['name']
        widgets = { 'name': forms.Select(attrs={'width': 30}) }

    def __init__(self, *args, **kwargs):
        super(AvailabilityAdminForm, self).__init__(*args, **kwargs)
        init_choices(self, 'name', AVAILABILITY)


class IntervieweeAdminForm(forms.ModelForm):

    class Meta:
        model = Interviewee
        fields = ['code', 'name', 'gender', 'age']
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
        fields = ['code', 'name', 'gender', 'age']
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
        fields = ['startYear', 'endYear']
        widgets = {'startYear': forms.Textarea(attrs={'rows': 1, 'cols': 20}),
                   'endYear': forms.Textarea(attrs={'rows': 1, 'cols': 20})}


class SpatialCoverageAdminForm(forms.ModelForm):

    class Meta:
        model = SpatialCoverage
        fields = ['country', 'place']
        widgets = {'country': forms.Select(attrs={'width': 30}),
                   'place': forms.Textarea(attrs={'rows': 1, 'cols': 80})  }

    def __init__(self, *args, **kwargs):
        super(SpatialCoverageAdminForm, self).__init__(*args, **kwargs)
        init_choices(self, 'country', COVERAGE_SPATIAL_COUNTRY)


class GenreAdminForm(forms.ModelForm):

    class Meta:
        model = Genre
        fields = ['name']
        widgets = { 'name': forms.Select(attrs={'width': 30}) }

    def __init__(self, *args, **kwargs):
        super(GenreAdminForm, self).__init__(*args, **kwargs)
        init_choices(self, 'name', INTERVIEW_GENRE)
        self.fields['name'].initial = choice_value("interview.genre", "interviews")


class AnnotationAdminForm(forms.ModelForm):

    class Meta:
        model = Annotation
        fields = ['type', 'mode', 'format']
        widgets = { 'type':   forms.Select(attrs={'width': 30}),
                    'mode':   forms.Select(attrs={'width': 30}),
                    'format': forms.Select(attrs={'width': 30}) }

    def __init__(self, *args, **kwargs):
        super(AnnotationAdminForm, self).__init__(*args, **kwargs)
        init_choices(self, 'type', ANNOTATION_TYPE)
        init_choices(self, 'mode', ANNOTATION_MODE)
        init_choices(self, 'format', ANNOTATION_FORMAT)
        self.fields['type'].initial = choice_value("annotation.type", "orthographicTranscription")


class AnonymisationAdminForm(forms.ModelForm):

    class Meta:
        model = Anonymisation
        fields = ['name']
        widgets = { 'name': forms.Select(attrs={'width': 30}) }

    def __init__(self, *args, **kwargs):
        super(AnonymisationAdminForm, self).__init__(*args, **kwargs)
        init_choices(self, 'name', ANONYMISATION)


class DescriptorAdminForm(forms.ModelForm):

    class Meta:
        model = Descriptor
        fields = ['identifier','projectTitle', 'interviewId', 'interviewDate', 'interviewLength', 'copyright','topicList', 'modality']

    def __init__(self, *args, **kwargs):
        super(DescriptorAdminForm, self).__init__(*args, **kwargs)
        init_choices(self, 'modality', INTERVIEW_MODALITY)
        self.fields['modality'].initial = choice_value("interview.modality", "spoken")


