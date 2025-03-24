import base64
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import List
from xml.etree.ElementTree import Element
import sys



NAMESPACE = "{urn:ietf:params:xml:ns:iris-transport}"



class XMLAttributeError(Exception):
    def __init__(self, message, line_num):
        self.message = message
        self.line_num = line_num
        super().__init__(message)

    def __str__(self):
        return f"{self.message} at line {self.line_num}"


class FileValidationError(Exception):
    def __init__(self, file_name):
        self.file_name = file_name


    def __str__(self):
        return f"File {self.file_name} failed validation"


class ElementError(Exception):
    def __init__(self, message, line_num):
        self.message = message
        self.line_num = line_num
        super().__init__(message)

    def __str__(self):
        return f"{self.message} at line {self.line_num}"


@dataclass
class AttribObject:
    name: str
    required: bool = False


@dataclass
class ElementObject:
    name: str
    min_occur: int = 1
    max_occur: int = 1


def isBase64(s):
    try:
        return base64.b64encode(base64.b64decode(s)).decode() == s
    except Exception:
        return False


def verify_attrib(element: Element, allowed_attrib: List[AttribObject]):
    keys = element.keys()
    validated_attrib = set()
    for attrib in allowed_attrib:
        count = keys.count(attrib.name)
        validated_attrib.add(attrib.name)
        if count < 1 and attrib.required:
            raise XMLAttributeError(f"Missing required attribute: {attrib.name}.", 0)
    invalid_attrib = set(keys) - validated_attrib
    if invalid_attrib != set():
        raise XMLAttributeError(f"Unexpected attributes found: {invalid_attrib}", 0)


def verify_element(element: Element, required_elements: List[ElementObject]):
    for child in required_elements:
        element_list = element.findall(child.name)
        count = len(element_list)
        if (child.max_occur is not None) and (count > child.max_occur):
            raise ElementError(
                f"Too many occurences of element: {child.name}.(found: {count} max: {child.max_occur})",
                0,
            )
        if count < child.min_occur:
            raise ElementError(
                f"Missing required element: {child.name}. (found: {count}, required: {child.min_occur})",
                0,
            )
    expected_elements = {child.name for child in required_elements}
    actual_elements = {child.tag for child in element}
    if actual_elements - expected_elements != set():
        raise ElementError(
            f"Unexpected elements found: {actual_elements - expected_elements}", 0
        )


def validate_versions(root: Element):
    verify_attrib(root, [])
    verify_element(root, [ElementObject(f"{NAMESPACE}transferProtocol", 1, None)])
    for transferprotocol in root:
        validate_transferProtocol(transferprotocol)
        for application in transferprotocol:
            validate_application(application)

            for datamodel in application:
                validate_dataModel(datamodel)


def validate_transferProtocol(transferprotocol: Element):
    allowed_attrib = [
        AttribObject("protocolId", True),
        AttribObject("extensionIds"),
        AttribObject("authenticationIds"),
        AttribObject("responseSizeOctets"),
        AttribObject("requestSizeOctets"),
    ]

    verify_element(
        transferprotocol, [ElementObject(f"{NAMESPACE}application", 0, None)]
    )
    
    verify_attrib(transferprotocol, allowed_attrib)


def validate_application(application: Element):
    allowed_attrib = [AttribObject("protocolId", True), AttribObject("extensionIds")]
    verify_element(application, [ElementObject(f"{NAMESPACE}dataModel", 0, None)])
    verify_attrib(application, allowed_attrib)


def validate_dataModel(datamodel: Element):
    allowed_attrib = [AttribObject("protocolId", True), AttribObject("extensionIds")]
    verify_element(datamodel, [])
    verify_attrib(datamodel, allowed_attrib)


def verify_octetsType(element: Element):
    allowed_elements = [
        ElementObject(f"{NAMESPACE}exceedsMaximum", 0),
        ElementObject(f"{NAMESPACE}octets", 0),
    ]
    verify_element(element, allowed_elements)
    exceeds = element.find(f"{NAMESPACE}exceedsMaximum")
    octets = element.find(f"{NAMESPACE}octets")
    if exceeds is not None and octets is not None:
        raise ElementError('Cannot have both "exceedsMaximum" and "octets" types', 0)
    if octets is not None:
        verify_attrib(octets, [])
        verify_element(octets, [])
        value = octets.text
        try:
            clean_value = value.strip()
            int_value = int(clean_value)
            if int_value <= 0:
                raise ElementError(
                    f"Cannot have octets value less than or equal to 0. Value: {int_value}",
                    0,
                )
        except ValueError:
            raise ElementError(f"octets value is not an integer. Value: {value}", 0)

    elif exceeds is not None:
        verify_attrib(exceeds, [])
        verify_element(exceeds, [])


def validate_size(root: Element):
    allowed_elements = [
        ElementObject(f"{NAMESPACE}request", 0, 1),
        ElementObject(f"{NAMESPACE}response", 0, 1),
    ]
    verify_element(root, allowed_elements)
    verify_attrib(root, [])
    for child in root:
        verify_attrib(child, [])
        verify_octetsType(child)


def validate_authenticationSuccess(root: Element):
    allowed_elements = [
        ElementObject(f"{NAMESPACE}description", 0, None),
        ElementObject(f"{NAMESPACE}data", 0, 1),
    ]
    verify_element(root, allowed_elements)
    verify_attrib(root, [])
    description_languages = []
    for child in root:
        if child.tag == f"{NAMESPACE}description":
            verify_attrib(child, [AttribObject("language", True)])
            description_languages.append(child.attrib["language"])
        elif child.tag == f"{NAMESPACE}data":
            verify_attrib(child, [])
            if not isBase64(child.text):
                raise ElementError("Data value is not base 64", 0)
        verify_element(child, [])

    if len(description_languages) != len(set(description_languages)):
        raise ElementError(
            "Each description element does not have a unique language", 0
        )


def validate_authenticationFailure(root: Element):
    allowed_elements = [
        ElementObject(f"{NAMESPACE}description", 0, None),
    ]
    verify_element(root, allowed_elements)
    verify_attrib(root, [])
    description_languages = []
    for child in root:
        verify_attrib(child, [AttribObject("language", True)])
        verify_element(child, [])
        description_languages.append(child.attrib["language"])
    if len(description_languages) != len(set(description_languages)):
        raise ElementError(
            "Each description element does not have a unique language", 0
        )


def validate_other(root: Element):
    allowed_elements = [
        ElementObject(f"{NAMESPACE}description", 0, None),
    ]
    verify_element(root, allowed_elements)
    verify_attrib(root, [AttribObject("type", True)]) 
    description_languages = []
    for child in root:
        verify_attrib(child, [AttribObject("language", True)])
        verify_element(child, [])
        description_languages.append(child.attrib["language"])
    if len(description_languages) != len(set(description_languages)):
        raise ElementError(
            "Each description element does not have a unique language", 0
        )


def validate_xml(file_name="unknown file"):
    try:
        file = ET.parse(file_name)
        root = file.getroot()
    except ET.ParseError as e:
        return None
    except FileNotFoundError:
        return None

    name = re.sub(r"\{.*?\}", "", root.tag)
    if name == "versions":
        try:
            validate_versions(root)
        except (XMLAttributeError, ElementError) as e:
            raise FileValidationError(file_name) from e

    elif name == "size":
        try:
            validate_size(root)
        except (XMLAttributeError, ElementError) as e:
            raise FileValidationError(file_name) from e

    elif name == "authenticationSuccess":
        try:
            validate_authenticationSuccess(root)
        except (XMLAttributeError, ElementError) as e:
            raise FileValidationError(file_name) from e

    elif name == "authenticationFailure":
        try:
            validate_authenticationFailure(root)
        except (XMLAttributeError, ElementError) as e:
            raise FileValidationError(file_name) from e

    elif name == "other":
        try:
            validate_other(root)
        except (XMLAttributeError, ElementError) as e:
            raise FileValidationError(file_name) from e

    else:
        raise Exception("root not IRIS conformant")

validate_xml('/home/clark/repos/file-stream/FILES/other-example.xml')