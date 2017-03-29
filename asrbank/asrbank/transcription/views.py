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
from django.utils import timezone
import json
from datetime import datetime
from xml.dom import minidom
import xml.etree.ElementTree as ET
from lxml import etree
import os

from asrbank.settings import APP_PREFIX, LANGUAGE_CODE_LIST, XSD_NAME
from asrbank.transcription.models import *
from asrbank.transcription.forms import *

# Local variables
XSI_CMD = "http://www.clarin.eu/cmd/"
XSD_ID = "clarin.eu:cr1:p_1459844210473"
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
        
            
def add_collection_xml(item_this, crp):
    """Add the collection information from [item_this] to XML element [crp]"""

    # title (1-n)
    add_element("1-n", item_this, "title", crp, foreign="name")
    # description (0-1)
    add_element("0-1", item_this, "description", crp)
    # owner (0-n)
    add_element("0-n", item_this, "owner", crp, foreign="name")
    # genre (0-n)
    add_element("0-n", item_this, "genre", crp, foreign="name", fieldchoice=GENRE_NAME)
    # languageDisorder(0-n)
    add_element("0-n", item_this, "languageDisorder", crp, foreign="name")
    # There's no return value -- all has been added to [crp]


def get_language(lngCode):
    if str(lngCode) == "493": 
        x = 1
    # Get the language string according to the field choice
    sLanguage = choice_english("language.name", lngCode).lower()
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
    order_cols = ['id', 'identifier']
    order_heads = [{'name': 'id', 'order': 'o=1', 'type': 'int'}, 
                   {'name': 'Identifier', 'order': 'o=2', 'type': 'str'}, 
                   {'name': 'Description', 'order': '', 'type': 'str'}]

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
        if sType == 'str':
            qs = Descriptor.objects.order_by(Lower(order))
        else:
            qs = Descriptor.objects.order_by(order)
        if not bAscending:
            qs = qs.reverse()
        context['overview_list'] = qs.select_related()
        context['order_heads'] = self.order_heads
        # Return the calculated context
        return context

    def convert_to_xml(self, context):
        """Convert all available descriptors to XML"""

        # Create a top-level element, including CMD, Header and Resources
        top = make_descriptor_top()

        # Start components and this collection component
        cmp     = ET.SubElement(top, "Components")
        # Add a <CorpusCollection> root that contains a list of <collection> objects
        colroot = ET.SubElement(cmp, "CorpusCollection")

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

