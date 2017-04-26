from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.contrib.contenttypes.models import ContentType
from django.core import serializers
from django.core.urlresolvers import resolve
from django.db.models import Q
from django.forms import Textarea
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django import forms
from functools import partial

import copy  # (1) use python copy
# import nested_admin
import logging

from asrbank.transcription.models import *
from asrbank.transcription.forms import *
from asrbank.settings import APP_PREFIX

MAX_IDENTIFIER_LEN = 10
logger = logging.getLogger(__name__)

def get_formfield_qs(modelThis, instanceThis, parentName, bNoEmpty = False):
    """Get the queryset for [modelThis]
    
    Restrict it to the field named [parentName] equalling [instanceThis]
    If [bNoEmpty] is FALSE and the filtered result is empty, then get a list of all
    instances from the [modelThis] that are not bound to [parentName] """

    # Perform the initial filtering of modelThis
    qs = modelThis.objects.filter(**{parentName: instanceThis})
    # Check if the filtered result is empty
    if not bNoEmpty and len(qs) == 0:
        # Get all the instances of [modelThis] that are not bound to [parentName]
        qs = modelThis.objects.filter(**{parentName: None})
    else:
        # Combine the filtered result with all unbound instances of [modelThis]
        # Note: this makes sure that NEWLY created instances are available
        qs = qs | modelThis.objects.filter(**{parentName: None})
    # Return the queryset that we have created
    return qs.select_related()

def copy_item(request=None):
    # Get the parameters from the request object
    sCurrent = request.GET['current']
    sModel = request.GET['model']
    original_pk = request.GET['id']

    # Determine what the model must be
    model = None
    if sModel == "resource":
        # Get the object
        original_obj = Resource.objects.get(id=original_pk)

        # Make a copy of this object and save it
        copy_obj = original_obj.get_copy()
        copy_obj.save()

        # Get the OWNER of the original object
        original_owner = Collection.objects.get(resource__id=original_pk)
        # Add the new Resource to this new owner
        original_owner.resource.add(copy_obj)

    elif sModel == "title":
        # Get the object
        original_obj = Title.objects.get(id=original_pk)

        # Make a copy of this object and save it
        copy_obj = original_obj.get_copy()
        copy_obj.save()

        # Get the OWNER of the original object
        original_owner = Collection.objects.get(title__id=original_pk)
        # Add the new Title to this new owner
        original_owner.title.add(copy_obj)

    elif sModel == "speechcorpus":
        # Get the object
        original_obj = SpeechCorpus.objects.get(id=original_pk)

        # Make a copy of this object and save it
        copy_obj = original_obj.get_copy()
        copy_obj.save()

        # Get the OWNER of the original object
        original_owner = Resource.objects.get(title__id=original_pk)
        # Add the new Title to this new owner
        original_owner.speechCorpus.add(copy_obj)

    elif sModel == "writtencorpus":
        # Get the object
        original_obj = WrittenCorpus.objects.get(id=original_pk)

        # Make a copy of this object and save it
        copy_obj = original_obj.get_copy()
        copy_obj.save()

        # Get the OWNER of the original object
        original_owner = Resource.objects.get(title__id=original_pk)
        # Add the new Title to this new owner
        original_owner.writtenCorpus.add(copy_obj)


    # Now redirect to the 'current' URL
    return redirect(sCurrent)


class LanguageInline(admin.TabularInline):
    model = Language
    form = LanguageAdminForm
    verbose_name = "Transcription language"
    verbose_name_plural = "Transcription language"
    # Define scope: [1-n]
    extra = 0
    min_num = 1
    insert_after = 'interviewLength'


class FileFormatInline(admin.TabularInline):
    model = FileFormat
    form = FileFormatAdminForm
    verbose_name = "File format"
    verbose_name_plural = "File formats"
    # Define scope: [0-n]
    extra = 0
    insert_after = 'interviewLength'


class AvailabilityInline(admin.TabularInline):
    model = Availability
    form = AvailabilityAdminForm
    verbose_name = "Availability"
    verbose_name_plural = "Availabilities"
    # Define scope: [0-n]
    extra = 0
    insert_after = 'interviewLength'


class IntervieweeInline(admin.TabularInline):
    model = Interviewee
    form = IntervieweeAdminForm
    verbose_name = "Interviewee"
    verbose_name_plural = "Interviewees"
    # Define scope: [1-n]
    extra = 0
    min_num = 1
    # Use 'copyright' when it is visible
    # insert_after = 'copyright'
    # Use 'interviewLength' otherwise
    insert_after = 'interviewLength'


class InterviewerInline(admin.TabularInline):
    model = Interviewer
    form = InterviewerAdminForm
    verbose_name = "Interviewer"
    verbose_name_plural = "Interviewers"
    # Define scope: [1-n]
    extra = 0
    min_num = 1
    # Use 'copyright' when it is visible
    # insert_after = 'copyright'
    # Use 'interviewLength' otherwise
    insert_after = 'interviewLength'


class TopicInline(admin.TabularInline):
    model = Topic
    form = TopicAdminForm
    verbose_name = "Topic"
    verbose_name_plural = "Topic list"
    # Define scope: [0-n]
    extra = 0
    validate_min = True
    insert_after = "interviewLength"


class TemporalCoverageInline(admin.TabularInline):
    model = TemporalCoverage
    form = TemporalCoverageAdminForm
    verbose_name = "Temporal coverage"
    verbose_name_plural = "Temporal coverages"
    # Define scope: [0-n]
    extra = 0
    insert_after = "interviewLength"


class SpatialCoverageInline(admin.TabularInline):
    model = SpatialCoverage
    form = SpatialCoverageAdminForm
    verbose_name = "Spatial coverage"
    verbose_name_plural = "Spatial coverages"
    # Define scope: [0-n]
    extra = 0
    insert_after = "interviewLength"


class GenreInline(admin.TabularInline):
    model = Genre
    form = GenreAdminForm
    verbose_name = "Genre"
    verbose_name_plural = "Genres"
    # Define scope: [1-n]
    extra = 0
    min_num = 1
    validate_min = True
    insert_after = "interviewLength"


class AnnotationInline(admin.TabularInline):
    model = Annotation
    form = AnnotationAdminForm
    verbose_name = "Annotation"
    verbose_name_plural = "Annotations"
    # Define scope: [0-n]
    extra = 0
    insert_after = "modality"


class AnonymisationInline(admin.TabularInline):
    model = Anonymisation
    form = AnonymisationAdminForm
    verbose_name = "Anonymisation"
    verbose_name_plural = "Anonymisations"
    # Define scope: [0-n]
    extra = 0
    insert_after = "modality"


class DescriptorAdmin(admin.ModelAdmin):

    model = Descriptor
    form = DescriptorAdminForm

    # Define the fields preliminarily -- full definition is done in [get_form()]
    fields = ('identifier','access', 'projectTitle', 'interviewId', 'interviewDate', 'interviewLength', 'copyright', 'modality',)

    # Note: the 'owner' can only be changed by the administrator
    #       (This statement depends on the user-status: exclude = ['owner']  )
    #       (See get_form() for details                                      )
    list_display = ['identifier_column', 'id', 'owner', 'access', 'projectTitle', 'interviewDate']
    search_fields = ['identifier', 'owner', 'projectTitle']
    list_filter = ['access']

    inlines = [TopicInline, LanguageInline, FileFormatInline, AvailabilityInline,
               IntervieweeInline, InterviewerInline,
               TemporalCoverageInline, SpatialCoverageInline,
               GenreInline, AnnotationInline, AnonymisationInline]
    # Any actions for the admin form
    actions = []
    # Make sure text areas are shown wide enough on this level
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 80})},
        }

    def get_ordering_field_columns():
        return self.ordering

    def get_form(self, request, obj=None, **kwargs):
        """Determine who can see which fields, and how the fields appear"""

        if request.user.is_superuser:
            self.exclude = []
            self.fieldsets  = ( ('System', {'fields': ('identifier', 'owner','access', )}),
                  ('Administrative', {'fields': ('projectTitle', 'interviewId', 'interviewDate', 'interviewLength', 'copyright', )}),
                  ('Descriptive',    {'fields': ('modality', )}),
                )
        else:
            self.exclude = ['owner']
            self.fieldsets  = ( ('System', {'fields': ('identifier', 'access', )}),
                  ('Administrative', {'fields': ('projectTitle', 'interviewId', 'interviewDate', 'interviewLength', 'copyright', )}),
                  ('Descriptive',    {'fields': ('modality', )}),
                )
        # Continue with regular form-loading
        form = super(DescriptorAdmin, self).get_form(request, obj, **kwargs)
        return form

    def save_model(self, request, obj, form, change):
        # Only supply owner if not specified
        if obj.owner == None or obj.owner.is_anonymous():
            obj.owner = request.user
        super(DescriptorAdmin, self).save_model(request, obj, form, change)

    def get_queryset(self, request):
        lstQ = []
        if not request.user.is_superuser:
            lstQ.append(Q(owner=request.user))
        qs = Descriptor.objects.filter(*lstQ).select_related()
        return qs

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
        # Make sure that the DEFAULT values of Genre and Language are saved too
        if formset.prefix == "genres" or formset.prefix == "languages":
            # Save all the genre instances
            for frmThis in formset.forms:
                # Save this instance
                frmThis.instance.save()
        for instance in instances:
            instance.save()
        formset.save_m2m()

    def response_add(self, request, obj, post_url_continue="../%s/"):
        if not '_continue' in request.POST:
            if '_addanother' in request.POST:
                return HttpResponseRedirect("/"+APP_PREFIX+"admin/transcription/descriptor/add")
            else:
                return HttpResponseRedirect("/"+APP_PREFIX+"overview/")
        else:
            return super(DescriptorAdmin, self).response_add(request, obj, post_url_continue)

    def response_change(self, request, obj):
        if not '_continue' in request.POST:
            if '_addanother' in request.POST:
                return HttpResponseRedirect("/"+APP_PREFIX+"admin/transcription/descriptor/add")
            else:
                return HttpResponseRedirect("/"+APP_PREFIX+"overview/")
        else:
            return super(DescriptorAdmin, self).response_change(request, obj)

class FieldChoiceAdmin(admin.ModelAdmin):
    readonly_fields=['machine_value']
    list_display = ['english_name','dutch_name','machine_value','field']
    list_filter = ['field']

    def save_model(self, request, obj, form, change):

        if obj.machine_value == None:
            # Check out the query-set and make sure that it exists
            qs = FieldChoice.objects.filter(field=obj.field)
            if len(qs) == 0:
                # The field does not yet occur within FieldChoice
                # Future: ask user if that is what he wants (don't know how...)
                # For now: assume user wants to add a new field (e.g: wordClass)
                # NOTE: start with '1'
                obj.machine_value = 1
            else:
                # Calculate highest currently occurring value
                highest_machine_value = max([field_choice.machine_value for field_choice in qs])
                # The automatic machine value we calculate is 1 higher
                obj.machine_value= highest_machine_value+1

        obj.save()


class HelpUrlFilter(SimpleListFilter):
    """Custom filter to divide the help items in those that have a URL and not"""

    title = 'Has a URL'
    parameter_name = 'has_url'

    def lookups(self, request, model_admin):
        return [('yes', 'yes'), ('no', 'no')]

    def queryset(self, request, queryset):
        """Return a filtered queryset"""

        if self.value() == 'yes':
            return queryset.exclude(help_url='')
        elif self.value() == 'no':
            return queryset.filter(help_url='')
        else:
            return queryset


class HelpChoiceAdmin(admin.ModelAdmin):
    list_display = ['field', 'display_name', 'searchable', 'help_url']
    list_filter = ['searchable', HelpUrlFilter]


# Models that serve others
admin.site.register(FieldChoice, FieldChoiceAdmin)
admin.site.register(HelpChoice, HelpChoiceAdmin)

# -- descriptor as a whole
admin.site.register(Descriptor, DescriptorAdmin)
