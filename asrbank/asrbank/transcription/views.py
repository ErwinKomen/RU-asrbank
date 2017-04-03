"""
Definition of views.
"""

from django.views.generic.detail import DetailView
from django.views.generic import ListView
from django.shortcuts import get_object_or_404, render
from django.http import HttpRequest, HttpResponse
from django.template import RequestContext, loader
from django.contrib.admin.templatetags.admin_list import result_headers
from django.db.models.functions import Lower
from django.db.models import Q
from django.utils import timezone
import json
from datetime import datetime
from xml.dom import minidom
import xml.etree.ElementTree as ET
from lxml import etree
import os

from asrbank.settings import APP_PREFIX, LANGUAGE_CODE_LIST, WRITABLE_DIR,XSD_NAME, COUNTRY_CODES
from asrbank.transcription.models import *
from asrbank.transcription.forms import *

# Local variables
XSI_CMD = "http://www.clarin.eu/cmd/"
XSD_ID = "clarin.eu:cr1:p_1487686159240"
XSI_XSD = "https://catalog.clarin.eu/ds/ComponentRegistry/rest/registry/1.1/profiles/" + XSD_ID + "/xsd/"

# General help functions
def add_element(optionality, item_this, el_name, crp, **kwargs):
    """Add element [el_name] from descriptor [item_this] under the XML element [crp]
    
    Note: make use of the options defined in [kwargs]
    """

    foreign = ""
    if "foreign" in kwargs: foreign = kwargs["foreign"]
    field_choice = ""
    if "fieldchoice" in kwargs: field_choice = kwargs["fieldchoice"]
    field_name = el_name
    if "field_name" in kwargs: field_name = kwargs["field_name"]
    item_this_el = getattr(item_this, field_name)
    sub_name = el_name
    if "subname" in kwargs: sub_name = kwargs["subname"]
    if optionality == "0-1" or optionality == "1":
        item_value = item_this_el
        if optionality == "1" or item_value != None:
            if foreign != "" and not isinstance(item_this_el, str):
                item_value = getattr(item_this_el, foreign)
            if field_choice != "": item_value = choice_english(field_choice, item_value)
            # Make sure the value is a string
            item_value = str(item_value)
            # Do we need to discern parts?
            if "part" in kwargs:
                arPart = item_value.split(":")
                iPart = kwargs["part"]
                if iPart == 1:
                    item_value = arPart[0]
                elif iPart == 2:
                    if len(arPart) == 2:
                        item_value = arPart[1]
                    else:
                        item_value = ""
            if item_value != "":
                descr_element = ET.SubElement(crp, sub_name)
                descr_element.text = item_value
    elif optionality == "1-n" or optionality == "0-n":
        # Test for obligatory foreign
        if foreign == "": return False
        for t in item_this_el.all():
            item_value = getattr(t, foreign)
            if field_choice != "": item_value = choice_english(field_choice, item_value)
            # Make sure the value is a string
            item_value = str(item_value)
            if item_value == "(empty)": 
                item_value = "unknown"
            else:
                title_element = ET.SubElement(crp, sub_name)
                title_element.text = item_value
    # Return positively
    return True
    
def make_descriptor_top():
    """Create the top-level elements for a descriptor"""

    # Define the top-level of the xml output
    topattributes = {'xmlns': "http://www.clarin.eu/cmd/" ,
                     'xmlns:xsd':"http://www.w3.org/2001/XMLSchema/",
                     'xmlns:xsi': "http://www.w3.org/2001/XMLSchema-instance/",
                     'xsi:schemaLocation': XSI_CMD + " " + XSI_XSD,
                     'CMDVersion':'1.1'}
    # topattributes = {'CMDVersion':'1.1'}
    top = ET.Element('CMD', topattributes)

    # Add a header
    hdr = ET.SubElement(top, "Header", {})
    mdSelf = ET.SubElement(hdr, "MdSelfLink")
    mdProf = ET.SubElement(hdr, "MdProfile")
    mdProf.text = XSD_ID
    # Add obligatory Resources
    rsc = ET.SubElement(top, "Resources", {})
    lproxy = ET.SubElement(rsc, "ResourceProxyList")
    # TODO: add resource proxy's under [lproxy]

    ET.SubElement(rsc, "JournalFileProxyList")
    ET.SubElement(rsc, "ResourceRelationList")
    # Return the resulting top-level element
    return top
                    
def add_descriptor_xml(item_this, main):
    """Add the DESCRIPTOR information from [item_this] to XML element [main]"""

    # [1] Project title
    add_element("1", item_this, "ProjectTitle", main, field_name="projectTitle")
    # [1] ID of the interview
    add_element("1", item_this, "InterviewId", main, field_name="interviewId")
    # [0-1] Date of the interview
    add_element("0-1", item_this, "InterviewDate", main, field_name="interviewDate")
    # [0-1] Length of the interview
    add_element("0-1", item_this, "InterviewLength", main, field_name="interviewLength")
    # [0-n] FileFormat
    add_element("0-n", item_this, "FileFormat", main, 
                field_name="fileformats", foreign="name", fieldchoice=AUDIOVIDEO_FORMAT)
    # [0-n] Availability
    add_element("0-n", item_this, "Availability", main, 
                field_name="availabilities", foreign="name", fieldchoice=AVAILABILITY)
    # [0-1] Copyright description
    add_element("0-1", item_this, "Copyright", main, field_name="copyright")
    # [0-1] Topic list
    add_element("0-1", item_this, "TopicList", main, field_name="topicList")
    # [1-n] Genre
    add_element("1-n", item_this, "Genre", main, 
                field_name="genres", foreign="name", fieldchoice=INTERVIEW_GENRE)
    # [1] Project title
    add_element("1", item_this, "Modality", main, field_name="modality", fieldchoice=INTERVIEW_MODALITY)
    # [0-n] Anonymisation level
    add_element("0-n", item_this, "Anonymisation", main, 
                field_name="anonymisations", foreign="name", fieldchoice=ANONYMISATION)
    # ==============================================================================
    # [1-n] Language of the transcription
    for lng_this in item_this.languages.all():
        (sLngName, sLngCode) = get_language(lng_this.name)
        # Validation
        if sLngCode == "" or sLngCode == None:
            bStop = True
        else:
            lngMain = ET.SubElement(main, "Language")
            lngMainName = ET.SubElement(lngMain, "LanguageName")
            lngMainName.text = sLngName
            lngMainCode = ET.SubElement(lngMain, "ISO639")
            lngMainCodeVal = ET.SubElement(lngMainCode, "iso-639-3-code")
            lngMainCodeVal.text = sLngCode
    # [1-n] Interviewee
    for wee_this in item_this.interviewees.all():
        # Start adding the sub-element
        wee_sub = ET.SubElement(main, "Interviewee")
        # [1] code
        add_element("1", wee_this, "Code", wee_sub, field_name="code")
        # [0-1] Name of the interviewee
        add_element("0-1", wee_this, "Name", wee_sub, field_name="name")
        # [0-1] Gender of the interviewee
        add_element("0-1", wee_this, "Gender", wee_sub, field_name="gender", fieldchoice=PARTICIPANT_GENDER)
        # [0-1] Age of the interviewee
        add_element("0-1", wee_this, "Age", wee_sub, field_name="age")
    # [1-n] Interviewer
    for wer_this in item_this.interviewers.all():
        # Start adding the sub-element
        wer_sub = ET.SubElement(main, "Interviewer")
        # [1] code
        add_element("1", wer_this, "Code", wer_sub, field_name="code")
        # [0-1] Name of the interviewer
        add_element("0-1", wer_this, "Name", wer_sub, field_name="name")
        # [0-1] Gender of the interviewer
        add_element("0-1", wer_this, "Gender", wer_sub, field_name="gender", fieldchoice=PARTICIPANT_GENDER)
        # [0-1] Age of the interviewer
        add_element("0-1", wer_this, "Age", wer_sub, field_name="age")
    # [0-n] Temporal coverage
    for cov_this in item_this.temporalcoverages.all():
        # Start adding the sub-element
        cov_sub = ET.SubElement(main, "TemporalCoverage")
        # [1] start year
        add_element("1", cov_this, "StartYear", cov_sub, field_name="startYear")
        # [1] end year
        add_element("1", cov_this, "EndYear", cov_sub, field_name="endYear")
    # [0-n] Spatial coverage
    for cov_this in item_this.spatialcoverages.all():
        # Start adding the sub-element
        cov_sub = ET.SubElement(main, "SpatialCoverage")
        # country (0-1)
        cntry = cov_this.country
        if cntry != None:
            # Look up the country in the list
            (sEnglish, sAlpha2) = get_country(cntry)
            # Set the values 
            cntMain = ET.SubElement(cov_sub, "Country")
            cntMainName = ET.SubElement(cntMain, "CountryName")
            cntMainCoding = ET.SubElement(cntMain, "CountryCoding")
            cntMainName.text = sEnglish
            cntMainCoding.text = sAlpha2
        # [0-1] place (=city)
        add_element("0-1", cov_this, "Place", cov_sub, field_name="place")
    # annotation (0-n)
    for ann_this in item_this.annotations.all(): 
        # Add this annotation element
        ann = ET.SubElement(main, "annotation")
        # [1]   type
        add_element("1", ann_this, "type", ann, fieldchoice=ANNOTATION_TYPE)
        # [0-1] mode
        add_element("0-1", ann_this, "mode", ann, fieldchoice=ANNOTATION_MODE)
        # [0-1] format
        add_element("0-1", ann_this, "format", ann, fieldchoice=ANNOTATION_FORMAT)


def get_country(cntryCode):
    # Get the country string according to field-choice
    sCountry = choice_english(COVERAGE_SPATIAL_COUNTRY, cntryCode).strip()
    sCountryAlt = sCountry + " (the)"
    # Walk all country codes
    for tplCountry in COUNTRY_CODES:
        # Check for country name or alternative country name
        if sCountry == tplCountry[1] or sCountryAlt == tplCountry[1]:
            # REturn the correct country name and code
            return (tplCountry[1], tplCountry[0])
    # Empty
    return (None, None)

def get_language(lngCode):
    if str(lngCode) == "493": 
        x = 1
    # Get the language string according to the field choice
    sLanguage = choice_english(INTERVIEW_LANGUAGE, lngCode).lower()
    # Walk all language codes
    for tplLang in LANGUAGE_CODE_LIST:
        # Check in column #2 for the language name (must be complete match)
        if sLanguage == tplLang[2].lower():
            # Return the language code from column #0
            return (sLanguage, tplLang[0])
    # Empty
    return (None, None)

def validateXml(xmlstr):
    """Validate an XML string against an XSD schema
    
    The first argument is a string containing the XML.
    The XSD schema that is being used must be present in the static files section.
    """

    # Get the XSD definition
    schema = getSchema()
    if schema == None: return False

    # Load the XML string into a document
    xml = etree.XML(xmlstr)

    # Perform the validation
    validation = schema.validate(xml)
    # Return a tuple with the boolean validation and a possible error log
    return (validation, schema.error_log, )

def getSchema():
    # Get the XSD file into an LXML structure
    fSchema = os.path.abspath(os.path.join(WRITABLE_DIR, "xsd", XSD_NAME))
    with open(fSchema, encoding="utf-8", mode="r") as f:  
        sText = f.read()                        
        # doc = etree.parse(f)
        doc = etree.XML(sText)                                                    
    
    # Load the schema
    try:                                                                        
        schema = etree.XMLSchema(doc)                                           
        return schema
    except lxml.etree.XMLSchemaParseError as e:                                 
        print(e)                                                              
        return None

def xsd_error_list(lError, sXmlStr):
    """Transform a list of XSD error objects into a list of strings"""

    lHtml = []
    lHtml.append("<html><body><h3>XML output errors</h3><table>")
    lHtml.append("<thead><th>line</th><th>column</th><th>level</th><th>domain</th><th>type</th><th>message</th></thead>")
    lHtml.append("<tbody>")
    for oError in lError:
        lHtml.append("<tr><td>" + str(oError.line) + "</td>" +
                     "<td>" +str(oError.column) + "</td>" +
                     "<td>" +oError.level_name + "</td>" + 
                     "<td>" +oError.domain_name + "</td>" + 
                     "<td>" +oError.type_name + "</td>" + 
                     "<td>" +oError.message + "</td>")
    lHtml.append("</tbody></table>")
    # Add the XML string
    lHtml.append("<h3>The XML file contents:</h3>")
    lHtml.append("<div class='rawxml'><pre class='brush: xml;'>" + sXmlStr.replace("<", "&lt;").replace(">", "&gt;") + "</pre></div>")
    # Finish the HTML feedback
    lHtml.append("</body></html>")
    return "\n".join(lHtml)

def xsd_error_as_simple_string(error):
    """
    Returns a string based on an XSD error object with the format
    LINE:COLUMN:LEVEL_NAME:DOMAIN_NAME:TYPE_NAME:MESSAGE.
    """
    parts = [
        error.line,
        error.column,
        error.level_name,
        error.domain_name,
        error.type_name,
        error.message
    ]
    return ':'.join([str(item) for item in parts])

def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'transcription/index.html',
        {
            'title':'Home Page',
            'year':datetime.now().year,
        }
    )

def contact(request):
    """Renders the contact page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'transcription/contact.html',
        {
            'title':'Contact',
            'message':'Henk van den Heuvel (H.vandenHeuvel@Let.ru.nl)',
            'year':datetime.now().year,
        }
    )

def about(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'transcription/about.html',
        {
            'title':'About',
            'message':'Radboud University Oral History metadata registry.',
            'year':datetime.now().year,
        }
    )

class DescriptorListView(ListView):
    """Listview of transcriptions"""

    model = Descriptor
    context_object_name='transcription'
    template_name = 'transcription/overview.html'
    order_cols = ['id', 'identifier', 'owner__name', 'projectTitle', 'interviewDate']
    order_heads = [{'name': 'id', 'order': 'o=1', 'type': 'int'}, 
                   {'name': 'Identifier', 'order': 'o=2', 'type': 'str'}, 
                   {'name': 'Owner', 'order': 'o=3', 'type': 'str'}, 
                   {'name': 'Project', 'order': 'o=4', 'type': 'str'}, 
                   {'name': 'Date', 'order': 'o=5', 'type': 'str'}]

    def render_to_response(self, context, **response_kwargs):
        """Check if downloading is needed or not"""
        sType = self.request.GET.get('submit_type', '')
        if sType == 'xml':
            return self.download_to_xml(context)
        else:
            return super(DescriptorListView, self).render_to_response(context, **response_kwargs)

    def get_context_data(self, **kwargs):
        # Get the base implementation first of the context
        context = super(DescriptorListView, self).get_context_data(**kwargs)
        # Add our own elements
        context['app_prefix'] = APP_PREFIX
        # context['static_root'] = STATIC_ROOT
        # Figure out which ordering to take
        order = 'identifier'
        initial = self.request.GET
        oUser = self.request.user
        bAscending = True
        sType = 'str'
        if 'o' in initial:
            iOrderCol = int(initial['o'])
            bAscending = (iOrderCol>0)
            iOrderCol = abs(iOrderCol)
            order = self.order_cols[iOrderCol-1]
            sType = self.order_heads[iOrderCol-1]['type']
            if bAscending:
                self.order_heads[iOrderCol-1]['order'] = 'o=-{}'.format(iOrderCol)
            else:
                # order = "-" + order
                self.order_heads[iOrderCol-1]['order'] = 'o={}'.format(iOrderCol)
        if self.request.user.is_authenticated():
            lstQ = []
            if not oUser.is_superuser:
                lstQ.append(Q(owner=oUser))
            if sType == 'str':
                qs = Descriptor.objects.filter(*lstQ).select_related().order_by(Lower(order))
            else:
                qs = Descriptor.objects.filter(*lstQ).select_related().order_by(order)
            if not bAscending:
                qs = qs.reverse()
        else:
            qs = None
        context['overview_list'] = qs# qs.select_related()
        context['order_heads'] = self.order_heads
        # Return the calculated context
        return context

    def convert_to_xml(self, context):
        """Convert all available descriptors to XML"""

        # Create a top-level element, including CMD, Header and Resources
        top = make_descriptor_top()

        # Start components and this collection component
        cmp     = ET.SubElement(top, "Components")
        # Add a <OHmetaDescriptor> root that contains a list of <collection> objects
        colroot = ET.SubElement(cmp, "OHmetaDescriptor")

        # Walk all the collections
        for col_this in Descriptor.objects.all():

            # Add a <collection> root for this collection
            crp = ET.SubElement(colroot, "collection")
            # Add the information in this collection to the xml
            add_collection_xml(col_this, crp)

        # Convert the XML to a string
        xmlstr = minidom.parseString(ET.tostring(top,encoding='utf-8')).toprettyxml(indent="  ")

        # Validate the XML against the XSD
        (bValid, oError) = validateXml(xmlstr)
        if not bValid:
            # Provide an error message
            return (False, xsd_error_list(oError, xmlstr))

        # Return this string
        return (True, xmlstr)
    
    def download_to_xml(self, context):
        """Make the XML representation of ALL descriptors downloadable"""

        # Get the XML of this collection
        (bValid, sXmlStr) = self.convert_to_xml(context)
        if bValid:
            # Create the HttpResponse object with the appropriate CSV header.
            response = HttpResponse(sXmlStr, content_type='text/xml')
            response['Content-Disposition'] = 'attachment; filename="ohmeta_all.xml"'
        else:
            # Return the error response
            response = HttpResponse(sXmlStr)

        # Return the result
        return response

    def get_queryset(self):

        # Get the parameters passed on with the GET request
        get = self.request.GET
        oUser = self.request.user

        # Start a list of query details
        lstQ = []
        # Possibly adapt the query to focus on tye current user
        if not oUser.is_superuser:
            lstQ.append(Q(owner=oUser))
        if self.request.user.is_authenticated():
            qs = Descriptor.objects.filter(*lstQ).select_related()
        else:
            qs = None

        return qs


class DescriptorDetailView(DetailView):
    """Details of a selected transcription descriptor"""

    model = Descriptor
    export_xml = True
    context_object_name='descriptor'

    def get_object(self):
        obj = super(DescriptorDetailView,self).get_object()
        self.instance = obj
        form = DescriptorAdminForm(instance=obj)
        return form

    def get_context_data(self, **kwargs):
        context = super(DescriptorDetailView, self).get_context_data(**kwargs)
        context['now'] = timezone.now()
        context['descriptor'] = self.instance
        return context

    def render_to_response(self, context, **response_kwargs):
        """Check if downloading is needed or not"""
        sType = self.request.GET.get('submit_type', '')
        if sType == 'xml':
            return self.download_to_xml(context)
        elif self.export_xml and sType != '':
            return self.render_to_xml(context)
        else:
            return super(DescriptorDetailView, self).render_to_response(context, **response_kwargs)
        
    def convert_to_xml(self, context):
        """Convert the 'descriptor' object from the context to XML"""

        # Create a top-level element, including CMD, Header and Resources
        top = make_descriptor_top()

        # Start components and this collection component
        cmp = ET.SubElement(top, "Components")
        # Add a <OHmetaDescriptor> root that contains a list of <collection> objects
        descrroot = ET.SubElement(cmp, "OHmetaDescriptor")

        # Access this particular collection
        descriptor_this = context['descriptor']

        # Add this collection to the xml
        add_descriptor_xml(descriptor_this, descrroot)

        # Convert the XML to a string
        xmlstr = minidom.parseString(ET.tostring(top,encoding='utf-8')).toprettyxml(indent="  ")

        # Validate the XML against the XSD
        (bValid, oError) = validateXml(xmlstr)
        if not bValid:
            # Get error messages for all the errors

            return (False, xsd_error_list(oError, xmlstr))

        # Return this string
        return (True, xmlstr)

    def download_to_xml(self, context):
        """Make the XML representation of this descriptor downloadable"""

        # Construct a file name based on the identifier
        itemThis = self.instance
        sFileName = 'oh-descriptor-{}'.format(getattr(itemThis, 'identifier'))
        # Get the XML of this collection
        (bValid, sXmlStr) = self.convert_to_xml(context)
        if bValid:
            # Create the HttpResponse object with the appropriate CSV header.
            response = HttpResponse(sXmlStr, content_type='text/xml')
            response['Content-Disposition'] = 'attachment; filename="'+sFileName+'.xml"'
        else:
            # Return the error response
            response = HttpResponse(sXmlStr)

        # Return the result
        return response

