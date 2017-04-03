"""Models for the transcription records.

A transcription item contains administrative and descriptive information.
The item has a number of characteristics.

"""

from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

import copy  # (1) use python copy
import sys


MAX_IDENTIFIER_LEN = 10
MAX_STRING_LEN = 255

PROJECT_TITLE = "project.title"
INTERVIEW_ID = "interview.id"
INTERVIEW_DATE = "interview.date"
INTERVIEW_LENGTH = "interview.length"
INTERVIEW_LANGUAGE = "interview.language"
AUDIOVIDEO_FORMAT = "interview.format"
AVAILABILITY = "interview.availability"
COPYRIGHT = "interview.copyright"
PARTICIPANT_CODE = "participant.code"
PARTICIPANT_NAME = "participant.name"
PARTICIPANT_GENDER = "participant.gender"
PARTICIPANT_AGE = "participant.age"
TOPICLIST = "interview.topiclist"
COVERAGE_TEMPORAL = "coverage.temporal"
COVERAGE_SPATIAL_PLACE = "coverage.spatial.city"
COVERAGE_SPATIAL_COUNTRY = "coverage.spatial.country"
INTERVIEW_GENRE = "interview.genre"
INTERVIEW_MODALITY = "interview.modality"
ANNOTATION_TYPE = "annotation.type"
ANNOTATION_MODE = "annotation.mode"
ANNOTATION_FORMAT = "annotation.format"
ANONYMISATION = "anonymisation"


class FieldChoice(models.Model):

    field = models.CharField(max_length=50)
    english_name = models.CharField(max_length=100)
    dutch_name = models.CharField(max_length=100)
    machine_value = models.IntegerField(help_text="The actual numeric value stored in the database. Created automatically.")

    def __str__(self):
        return "{}: {}, {} ({})".format(
            self.field, self.english_name, self.dutch_name, str(self.machine_value))

    class Meta:
        ordering = ['field','machine_value']


class HelpChoice(models.Model):
    """Define the URL to link to for the help-text"""
    
    field = models.CharField(max_length=200)        # The 'path' to and including the actual field
    searchable = models.BooleanField(default=False) # Whether this field is searchable or not
    display_name = models.CharField(max_length=50)  # Name between the <a></a> tags
    help_url = models.URLField(default='')          # THe actual help url (if any)

    def __str__(self):
        return "[{}]: {}".format(
            self.field, self.display_name)

    def Text(self):
        help_text = ''
        # is anything available??
        if (self.help_url != ''):
            if self.help_url[:4] == 'http':
                help_text = "See: <a href='{}'>{}</a>".format(
                    self.help_url, self.display_name)
            else:
                help_text = "{} ({})".format(
                    self.display_name, self.help_url)
        return help_text


def build_choice_list(field, position=None, subcat=None):
    """Create a list of choice-tuples"""

    choice_list = [];
    unique_list = [];   # Check for uniqueness

    try:
        # check if there are any options at all
        if FieldChoice.objects == None:
            # Take a default list
            choice_list = [('0','-'),('1','N/A')]
        else:
            for choice in FieldChoice.objects.filter(field__iexact=field):
                # Default
                sEngName = ""
                # Any special position??
                if position==None:
                    sEngName = choice.english_name
                elif position=='before':
                    # We only need to take into account anything before a ":" sign
                    sEngName = choice.english_name.split(':',1)[0]
                elif position=='after':
                    if subcat!=None:
                        arName = choice.english_name.partition(':')
                        if len(arName)>1 and arName[0]==subcat:
                            sEngName = arName[2]

                # Sanity check
                if sEngName != "" and not sEngName in unique_list:
                    # Add it to the REAL list
                    choice_list.append((str(choice.machine_value),sEngName));
                    # Add it to the list that checks for uniqueness
                    unique_list.append(sEngName)

            choice_list = sorted(choice_list,key=lambda x: x[1]);
    except:
        print("Unexpected error:", sys.exc_info()[0])
        choice_list = [('0','-'),('1','N/A')];

    # Signbank returns: [('0','-'),('1','N/A')] + choice_list
    # We do not use defaults
    return choice_list;

def choice_english(field, num):
    """Get the english name of the field with the indicated machine_number"""

    try:
        result_list = FieldChoice.objects.filter(field__iexact=field).filter(machine_value=num)
        if (result_list == None):
            return "(No results for "+field+" with number="+num
        return result_list[0].english_name
    except:
        return "(empty)"

def choice_value(field, sEnglish):
    """Get the machine value of the field with the indicated english_name"""

    try:
        result_list = FieldChoice.objects.filter(field__iexact=field).filter(english_name__iexact=sEnglish)
        if (result_list == None or len(result_list) == 0):
            return -1
        return result_list[0].machine_value
    except:
        return -1

def m2m_combi(items):
    try:
        if items == None:
            sBack = ''
        else:
            qs = items.all()
            sBack = '-'.join([str(thing) for thing in qs])
        return sBack
    except:
        return "(exception: {})".format(sys.exc_info()[0])

def get_instance_copy(item):
    new_copy = copy.copy(item)
    new_copy.id = None          # Reset the id
    new_copy.save()             # Save it preliminarily
    return new_copy

def copy_m2m(inst_src, inst_dst, field, lst_m2m = None):
    # Copy M2M relationship: conversationalType    
    for item in getattr(inst_src, field).all():
        newItem = get_instance_copy(item)
        # Possibly copy more m2m
        if lst_m2m != None:
            for deeper in lst_m2m:
                copy_m2m(item, newItem, deeper)
        getattr(inst_dst, field).add(newItem)

def get_help(field):
    """Create the 'help_text' for this element"""

    # find the correct instance in the database
    help_text = ""
    try:
        entry_list = HelpChoice.objects.filter(field__iexact=field)
        entry = entry_list[0]
        # Note: only take the first actual instance!!
        help_text = entry.Text()
    except:
        help_text = "Sorry, no help available for " + field

    return help_text


class Language(models.Model):
    """Language that is used in a transcription"""

    # [1] Each language has a name
    name = models.CharField("Language in collection", choices=build_choice_list(INTERVIEW_LANGUAGE), max_length=5, 
                            help_text=get_help(INTERVIEW_LANGUAGE), default='0')
    # [1]     Each descriptor can have [0-n] languages associated with it
    descriptor = models.ForeignKey("Descriptor", blank=False, null=False, default=1, related_name="languages")

    def __str__(self):
        idt = self.descriptor.identifier
        sBack = "[{}] {}".format(idt,choice_english(INTERVIEW_LANGUAGE, self.name))
        return sBack


class FileFormat(models.Model):
    """Format of an audio/video file"""

    # [1] Each language has a name
    name = models.CharField("Format of audio/video file", choices=build_choice_list(AUDIOVIDEO_FORMAT), max_length=5, 
                            help_text=get_help(AUDIOVIDEO_FORMAT), default='0')
    # [1]     Each descriptor can have [0-n] file formats associated with it
    descriptor = models.ForeignKey("Descriptor", blank=False, null=False, default=1, related_name="fileformats")

    def __str__(self):
        idt = self.descriptor.identifier
        sBack = "[{}] {}".format(idt,choice_english(AUDIOVIDEO_FORMAT, self.name))
        return sBack


class Availability(models.Model):
    """Availability description"""

    class Meta:
        verbose_name_plural = "Availability descriptions"

    name = models.CharField("Availability", choices=build_choice_list(AVAILABILITY), max_length=5, help_text=get_help(AVAILABILITY), default='0')
    # [1]     Each descriptor can have [0-n] availability descriptors associated with it
    descriptor = models.ForeignKey("Descriptor", blank=False, null=False, default=1, related_name="availabilities")

    def __str__(self):
        idt = self.descriptor.identifier
        sBack = "[{}] {}".format(idt,choice_english(AVAILABILITY, self.name))
        return sBack


class Participant(models.Model):
    """A participant of an interview"""
    
    # [1] Obligatory code
    code = models.CharField("Code for this person",  max_length=MAX_STRING_LEN, blank=False, help_text=get_help(PARTICIPANT_CODE))
    # [0-1] Name of the participant
    name = models.CharField("Name of the person",  max_length=MAX_STRING_LEN, blank=True, help_text=get_help(PARTICIPANT_NAME))
    # [0-1; closed] Gender of the participant
    gender = models.CharField("Gender of the person", choices=build_choice_list(PARTICIPANT_GENDER), max_length=5, 
                              help_text=get_help(PARTICIPANT_GENDER), default='0', blank=True)
    # [0-1] Age of the participant as STRING
    age = models.CharField("Age of the person",  max_length=MAX_STRING_LEN, blank=True, help_text=get_help(PARTICIPANT_AGE))

    def __str__(self):
        return self.code


class Interviewee(Participant):

    class Meta:
        verbose_name_plural = "Persons that were interviewed"

    # [1]     Each descriptor can have [0-n] interviewees associated with it
    descriptor = models.ForeignKey("Descriptor", blank=False, null=False, default=1, related_name="interviewees")

    def __str__(self):
        idt = self.descriptor.identifier
        sBack = "[{}] {}".format(idt,self.code)
        return sBack


class Interviewer(Participant):

    class Meta:
        verbose_name_plural = "Interviewers"

    # [1]     Each descriptor can have [0-n] interviewers associated with it
    descriptor = models.ForeignKey("Descriptor", blank=False, null=False, default=1, related_name="interviewers")

    def __str__(self):
        idt = self.descriptor.identifier
        sBack = "[{}] {}".format(idt,self.code)
        return sBack


class TemporalCoverage(models.Model):
    """Temporal coverage of a transcription"""

    class Meta:
        verbose_name_plural = "Spatial coverages"

    # == Start year: yyyy
    startYear = models.CharField("First year covered by the transcription", max_length=20, default=str(datetime.now().year))
    # == End year: yyyy
    endYear = models.CharField("Last year covered by the transcription", max_length=20, default=str(datetime.now().year))
    # [1]     Each descriptor can have [0-n] spatial coverages associated with it
    descriptor = models.ForeignKey("Descriptor", blank=False, null=False, default=1, related_name="temporalcoverages")

    def __str__(self):
        idt = self.descriptor.identifier
        sBack = "[{}] {}-{}".format(idt,self.startYear, self.endYear)
        return sBack


class SpatialCoverage(models.Model):
    """Spatial coverage of a transcription"""

    class Meta:
        verbose_name_plural = "Spatial coverages"

    # == country (0-1;c) (name+ISO-3166 code)
    country = models.CharField("Country included in this spatial coverage", choices=build_choice_list(COVERAGE_SPATIAL_COUNTRY), max_length=5, help_text=get_help(COVERAGE_SPATIAL_COUNTRY), default='0')
    # [0-1] place
    place = models.CharField("Place (city) for this spatial coverage", max_length=80, help_text=get_help(COVERAGE_SPATIAL_PLACE), blank=True)
    # [1]     Each descriptor can have [0-n] spatial coverages associated with it
    descriptor = models.ForeignKey("Descriptor", blank=False, null=False, default=1, related_name="spatialcoverages")

    def __str__(self):
        idt = self.descriptor.identifier
        sBack = "[{}] {}".format(idt,choice_english(COVERAGE_SPATIAL_COUNTRY, self.country))
        return sBack


class Genre(models.Model):
    """Genre of transcription as a whole"""

    # (1; c)
    name = models.CharField("Genre of this transcription", choices=build_choice_list(INTERVIEW_GENRE), max_length=5, help_text=get_help(INTERVIEW_GENRE), default='0')
    # [1]     Each descriptor can have [1-n] genres
    descriptor = models.ForeignKey("Descriptor", blank=False, null=False, default=1, related_name="genres")

    def __str__(self):
        idt = self.descriptor.identifier
        return "[{}] {}".format(idt,choice_english(INTERVIEW_GENRE, self.name))


class Annotation(models.Model):
    """Description of one annotation layer in a transcription"""
    
    # [1] default = orthography
    type = models.CharField("Kind of annotation", choices=build_choice_list(ANNOTATION_TYPE), max_length=5, 
                            help_text=get_help(ANNOTATION_TYPE), default='0')
    # [0-1]
    mode = models.CharField("Annotation mode", choices=build_choice_list(ANNOTATION_MODE), max_length=5, 
                            help_text=get_help(ANNOTATION_MODE), blank = True)
    # [0-1]
    format = models.CharField("Annotation format", choices=build_choice_list(ANNOTATION_FORMAT), max_length=5, 
                              help_text=get_help(ANNOTATION_FORMAT), blank = True)
    # [1]     Each descriptor can have [0-n] annotations
    descriptor = models.ForeignKey("Descriptor", blank=False, null=False, default=1, related_name="annotations")

    def __str__(self):
        idt = self.descriptor.identifier
        sType = choice_english(self.type)
        sMode = "-"
        sFormat = "-"
        if self.mode == None: sMode = choice_english(self.mode)
        if self.format == None: sFormat = choice_english(self.format)
        return "[{}] {}-{}-{}".format(idt, sType, sMode, sFormat)


class Anonymisation(models.Model):
    """Anonymisation level of the transcription"""

    class Meta:
        verbose_name_plural = "Anonymisation levels"

    # (1; c)
    name = models.CharField("Anonymisation level of the transcription", choices=build_choice_list(ANONYMISATION), max_length=5, 
                            help_text=get_help(ANONYMISATION), default='0')
    # [1]     Each descriptor can have [0-n] anonymisation levels
    descriptor = models.ForeignKey("Descriptor", blank=False, null=False, default=1, related_name="anonymisations")

    def __str__(self):
        idt = self.descriptor.identifier
        return "[{}] {}".format(idt,choice_english(ANONYMISATION, self.name))


class Descriptor(models.Model):
    """Description of the metadata of one OH transcription"""

    # INTERNAL FIELD: identifier (1)
    identifier = models.CharField("Unique short descriptor identifier (10 characters max)", max_length=MAX_IDENTIFIER_LEN, default='-')

    # INTERNAL FIELD: Owner of this descriptor (1)
    owner = models.ForeignKey(User, blank=False, null=False)

    # ------------ ADMINISTRATIVE --------------
    # [1] Project title
    projectTitle = models.CharField("Project title", max_length=MAX_STRING_LEN, blank=False, 
                                    help_text=get_help(PROJECT_TITLE), default="-")
    # [1] ID of the interview
    interviewId = models.CharField("Interview ID", max_length=MAX_STRING_LEN, blank=False, 
                                   help_text=get_help(INTERVIEW_ID), default="-")
    # [0-1; YYYY-MM-DD]
    interviewDate = models.DateField("Date of the interview", default=datetime.today, blank=True, help_text=get_help(INTERVIEW_DATE))
    # [0-1; HH:MM:SS]
    interviewLength = models.TimeField("Length in time of the interview", default="00:00:00", blank=True, help_text=get_help(INTERVIEW_LENGTH))
    # [1-n; closed] - Language
    # [0-n; closed] - FileFormat
    # [0-n; closed] - Availability
    # [0-1] Copyright description
    copyright = models.TextField("Copyright for this transcription", blank=True, help_text=get_help(COPYRIGHT))

    # ------------- DESCRIPTIVE ---------------
    # [1-n]  - Interviewee
    # [1-n]  - Interviewer

    # [0-1]  - Topic list
    topicList =  models.TextField("List of topics for this transcription", blank=True, help_text=get_help(TOPICLIST))
    # [0-n; YYYY-YYYY]     - Temporal coverages
    # [0-n; Country;Place] - Spatial coverages
    # [1-n; closed]        - Genres

    # [1] Modality
    modality = models.CharField("Transcription modality", choices=build_choice_list(INTERVIEW_MODALITY), max_length=5, 
                            help_text=get_help(INTERVIEW_MODALITY), default='0')
    # [0-n] Annotations
    # [0-n] Anonymisation levels


    def __str__(self):
        return self.identifier

    @classmethod
    def create(cls, **kwargs):
        """Create a new instance of Descriptor"""

        # Create this new instance
        instance = cls(kwargs)

        # Add default one-to-many relations, as appropriate...

        # Return the result
        return instance

    def save(self, **kwargs):
        # Do the initial saving
        instance = super(Descriptor, self).save(**kwargs)
        # Check for obligatory 1-n relations
        genres = self.genres.all()


