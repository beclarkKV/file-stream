import base64
import re
import xml.etree.ElementTree as ET
from typing import List
from typing import Tuple
from xml.etree.ElementTree import Element


class XMLAttributeError(Exception):
    def __init__(self, message, file_name, line_num):
        self.message = message
        self.file_name = file_name
        self.line_num = line_num
        super().__init__(message)
    def __str__(self):
        return f"{self.message} in {self.file_name} at line {self.line_num}"
    

class ElementError(Exception):
    def __init__(self, message, file_name, line_num):
        self.message = message
        self.file_name = file_name
        self.line_num = line_num
        super().__init__(message)
    def __str__(self):
        return f"{self.message} in {self.file_name} at line {self.line_num}"    


class AttribObject:
    def __init__(self, name: str, required=False):
        self.name = name
        self.required = required


class ElementObject:
    def __init__(self, name: str, min_occur=1, max_occur=1):
        self.name = name
        self.min_occur = min_occur
        self.max_occur = max_occur


def isBase64(s):
    try:
        return base64.b64encode(base64.b64decode(s)).decode() == s
    except Exception:
        return False


def verify_attrib(element: Element, allowed_attrib: List[AttribObject], file_name):
    keys = element.keys()
    validated_attrib = set()
    for attrib in allowed_attrib:
        count = keys.count(attrib.name)
        validated_attrib.add(attrib.name)
        if count < 1 and attrib.required:
            raise XMLAttributeError(f"Missing required attribute: {attrib.name}.", file_name, 0)
    invalid_attrib = set(keys) - validated_attrib
    if invalid_attrib != set():
        raise XMLAttributeError(f"Unexpected attributes found: {invalid_attrib}", file_name, 0)
    

def verify_element(element: Element, required_elements: List[ElementObject], file_name):
    for child in required_elements:
        element_list = element.findall(child.name)
        count = len(element_list)
        if (child.max_occur is not None) and (count > child.max_occur):
            raise ElementError(f"Too many occurences of element: {child.name}.(found: {count} max: {child.max_occur})", file_name, 0)
        if count < child.min_occur:
            raise ElementError(f"Missing required element: {child.name}. (found: {count}, required: {child.min_occur})", file_name, 0)
    expected_elements = {child.name for child in required_elements}
    actual_elements = {child.tag for child in element}
    if actual_elements - expected_elements != set():
        raise ElementError(f"Unexpected elements found: {actual_elements - expected_elements}", file_name, 0)


def validate_versions(root: Element, file_name):
    verify_attrib(root, [], file_name)
    # verifies the children of the versions root are all = to transferprotocol
    verify_element(root, [ElementObject("{urn:ietf:params:xml:ns:iris-transport}transferProtocol", 1, None)], file_name)
    for transferprotocol in root:
        validate_transferProtocol(transferprotocol, file_name)
        for application in transferprotocol:
            validate_application(application, file_name)
        
            for datamodel in application:
                validate_dataModel(datamodel, file_name)


def validate_transferProtocol(transferprotocol: Element, file_name):
    allowed_attrib = [
        AttribObject("protocolId", True),
        AttribObject("extensionIds"),
        AttribObject("authenticationIds"),
        AttribObject("responseSizeOctets"),
        AttribObject("requestSizeOctets"),
    ]
    verify_element(transferprotocol, [ElementObject("{urn:ietf:params:xml:ns:iris-transport}application", 0, None)], file_name)
    verify_attrib(transferprotocol, allowed_attrib, file_name)


def validate_application(application: Element, file_name):
    allowed_attrib = [AttribObject("protocolId", True), AttribObject("extensionIds")]
    verify_element(application, [ElementObject("{urn:ietf:params:xml:ns:iris-transport}dataModel", 0, None)], file_name)
    verify_attrib(application, allowed_attrib, file_name)


def validate_dataModel(datamodel: Element, file_name):
    allowed_attrib = [AttribObject("protocolId", True), AttribObject("extensionIds")]
    verify_element(datamodel, [], file_name)
    verify_attrib(datamodel, allowed_attrib, file_name)


def verify_octetsType(element: Element, file_name):
    allowed_elements = [ElementObject("{urn:ietf:params:xml:ns:iris-transport}exceedsMaximum",0), ElementObject("{urn:ietf:params:xml:ns:iris-transport}octets",0)]
    verify_element(element, allowed_elements, file_name)
    exceeds = element.find("{urn:ietf:params:xml:ns:iris-transport}exceedsMaximum")
    octets = element.find("{urn:ietf:params:xml:ns:iris-transport}octets")
    if exceeds is not None and octets is not None:
        raise ElementError('Cannot have both "exceedsMaximum" and "octets" types', file_name, 0)
    if octets is not None:
        verify_attrib(octets, [], file_name)
        verify_element(octets, [], file_name)
        value = octets.text
        try:
            clean_value = value.strip() 
            int_value = int(clean_value)  
            if int_value <= 0:
                raise ElementError(f"Cannot have octets value less than or equal to 0. Value: {int_value}", file_name, 0)
        except ValueError:
            raise ElementError(f"octets value is not an integer. Value: {value}", file_name, 0)

    elif exceeds is not None:
        verify_attrib(exceeds, [], file_name)
        verify_element(exceeds, [], file_name)


def validate_size(root: Element, file_name):
    allowed_elements = [
        ElementObject("{urn:ietf:params:xml:ns:iris-transport}request", 0, 1),
        ElementObject("{urn:ietf:params:xml:ns:iris-transport}response", 0, 1),
    ]
    verify_element(root, allowed_elements, file_name)
    verify_attrib(root, [], file_name)
    for child in root:
        verify_attrib(child, [], file_name)
        verify_octetsType(child, file_name)


def validate_authenticationSuccess(root: Element, file_name):
    allowed_elements = [
        ElementObject("{urn:ietf:params:xml:ns:iris-transport}description", 0, None),
        ElementObject("{urn:ietf:params:xml:ns:iris-transport}data", 0, 1),
    ]
    verify_element(root, allowed_elements, file_name)
    verify_attrib(root, [], file_name)
    description_languages = []
    for child in root:
        if child.tag == "{urn:ietf:params:xml:ns:iris-transport}description":
            verify_attrib(child, [AttribObject("language", True)], file_name)
            description_languages.append(child.attrib['language'])
        elif child.tag == "{urn:ietf:params:xml:ns:iris-transport}data":
            verify_attrib(child, [], file_name)
            if not isBase64(child.text):
                raise ElementError("Data value is not base 64", file_name, 0)
        verify_element(child, [], file_name)
    if len(description_languages) != len(set(description_languages)):
        raise ElementError("Each description element does not have a unique language", file_name, 0)


def validate_authenticationFailure(root: Element, file_name):
    allowed_elements = [
        ElementObject("{urn:ietf:params:xml:ns:iris-transport}description", 0, None),
    ]
    verify_element(root, allowed_elements, file_name)
    verify_attrib(root, [], file_name)
    description_languages = []
    for child in root:
        verify_attrib(child, [AttribObject("language", True)], file_name)
        verify_element(child, [], file_name)
        description_languages.append(child.attrib['language'])
    if len(description_languages) != len(set(description_languages)):
        raise ElementError("Each description element does not have a unique language", file_name, 0)


def validate_other(root: Element, file_name):
    allowed_elements = [
        ElementObject("{urn:ietf:params:xml:ns:iris-transport}description", 0, None),
    ]
    verify_element(root, allowed_elements, file_name)
    verify_attrib(root, [AttribObject('type', True)], file_name)
    description_languages = []
    for child in root:
        verify_attrib(child, [AttribObject("language", True)], file_name)
        verify_element(child, [], file_name)
        description_languages.append(child.attrib['language'])
    if len(description_languages) != len(set(description_languages)):
        raise ElementError("Each description element does not have a unique language", file_name, 0)


def validate_xml(file_name = 'unknown file'):


    try:
        file = ET.parse(file_name)
        root = file.getroot()
    except ET.ParseError as e:
        print(f"XML parsing error: {e}")
        return False
    except FileNotFoundError:
        print("Error: File not found")
        return False

    name = re.sub(r"\{.*?\}", "", root.tag)
    if name == "versions":
        validate_versions(root, file_name)

    elif name == "size":
        validate_size(root, file_name)

    elif name == "authenticationSuccess":
        validate_authenticationSuccess(root, file_name)

    elif name == "authenticationFailure":
        validate_authenticationFailure(root, file_name)

    elif name == "other":
        validate_other(root, file_name)

    else:
        raise ValueError("not a iris conformant xml")