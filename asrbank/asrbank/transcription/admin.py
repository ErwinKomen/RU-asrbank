from django.contrib import admin
import nested_admin
from django.db.models import Q
from django import forms
from django.core.urlresolvers import resolve
from django.forms import Textarea
from django.shortcuts import redirect
from asrbank.transcription.models import *
from asrbank.settings import APP_PREFIX
from functools import partial
from django.core import serializers
from django.contrib.contenttypes.models import ContentType
import copy  # (1) use python copy
import logging

MAX_IDENTIFIER_LEN = 10
logger = logging.getLogger(__name__)

def init_choices(obj, sFieldName, sSet):
    if (obj.fields != None and sFieldName in obj.fields):
        obj.fields[sFieldName].choices = build_choice_list(sSet)
        obj.fields[sFieldName].help_text = get_help(sSet)

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


class DescriptorAdmin(nested_admin.NestedModelAdmin):
    fieldsets = ( ('System', {'fields': ('identifier',  )}),
                  ('Administrative', {'fields': (  )}),
                  ('Descriptive',    {'fields': (  )}),
                )

    list_display = ['identifier', 'id']
    search_fields = ['identifier']

    inlines = []

    actions = []
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 80})},
        }


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
                # NOTE: start with '0'
                obj.machine_value = 0
            else:
                # Calculate highest currently occurring value
                highest_machine_value = max([field_choice.machine_value for field_choice in qs])
                # The automatic machine value we calculate is 1 higher
                obj.machine_value= highest_machine_value+1

        obj.save()


# Models that serve others
admin.site.register(FieldChoice, FieldChoiceAdmin)
admin.site.register(HelpChoice)

# -- descriptor as a whole
admin.site.register(Descriptor, DescriptorAdmin)
