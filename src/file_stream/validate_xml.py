import base64
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import List
from xml.etree.ElementTree import Element

from loguru import logger

from file_stream.exceptions import ElementError
from file_stream.exceptions import FileValidationError
from file_stream.exceptions import XMLAttributeError


NAMESPACE = "{urn:ietf:params:xml:ns:iris-transport}"


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
    except:
        return False


def verify_attrib(element: Element, allowed_attrib: List[AttribObject]):
    logger.trace("verifying correct attributes")
    keys = element.keys()
    validated_attrib = check_required_attrib(allowed_attrib, keys)
    invalid_attrib = set(keys) - set(validated_attrib)
    if invalid_attrib != set():
        raise XMLAttributeError(f"Unexpected attributes found: {invalid_attrib}", 0)
    logger.debug("attributes valid")


def check_required_attrib(
    allowed_attrib: List[AttribObject], actual_attrib: list
) -> list:
    validated_attrib = []
    for attrib in allowed_attrib:
        count = actual_attrib.count(attrib.name)
        validated_attrib.append(attrib.name)
        if count < 1 and attrib.required:
            raise XMLAttributeError(f"Missing required attribute: {attrib.name}.", 0)
    return validated_attrib


def verify_element(element: Element, required_elements: List[ElementObject]):
    logger.trace("verifying correct children")
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
    logger.debug("children valid")


def validate_versions(root: Element):
    logger.trace("Enter verify 'versions' element")
    verify_attrib(root, [])
    verify_element(root, [ElementObject(f"{NAMESPACE}transferProtocol", 1, None)])
    for transferprotocol in root:
        logger.trace("Enter verify 'transferProtocol' element")
        validate_transferProtocol(transferprotocol)
        for application in transferprotocol:
            logger.trace("Enter verify 'application' element")
            validate_application(application)

            for datamodel in application:
                logger.trace("Enter verify 'dataModel' element")
                validate_dataModel(datamodel)
            logger.success("'application' element valid")
        logger.success("'transferProtocol' element valid")
    logger.success("'versions' element is valid")


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
    logger.success("'dataModel' element valid")


def verify_octetsType(element: Element):
    logger.trace("Verifying octets type is valid")
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
        verify_octets_child(octets)

    elif exceeds is not None:
        verify_attrib(exceeds, [])
        verify_element(exceeds, [])
    logger.debug("octets type is valid")

def verify_octets_child(octets: Element):
    verify_attrib(octets, [])
    verify_element(octets, [])
    value = octets.text
    verify_octets_value(value)

def verify_octets_value(value: str):
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

def validate_size(root: Element):
    allowed_elements = [
        ElementObject(f"{NAMESPACE}request", 0, 1),
        ElementObject(f"{NAMESPACE}response", 0, 1),
    ]
    logger.trace("Enter verify 'size' element")
    verify_element(root, allowed_elements)
    verify_attrib(root, [])
    for child in root:
        logger.trace(f"Enter verify '{child.tag[len(NAMESPACE):]}' element")
        verify_attrib(child, [])
        verify_octetsType(child)
        logger.success(f"'{child.tag[len(NAMESPACE):]}' element is valid")
    logger.success("'size' element is valid")


def validate_authenticationSuccess(root: Element):
    allowed_elements = [
        ElementObject(f"{NAMESPACE}description", 0, None),
        ElementObject(f"{NAMESPACE}data", 0, 1),
    ]
    logger.trace("Enter verify 'authenticationSuccess' element")
    verify_element(root, allowed_elements)
    verify_attrib(root, [])
    description_languages = []
    for child in root:
        if child.tag == f"{NAMESPACE}description":
            logger.trace("Enter verify 'description' element")
            verify_attrib(child, [AttribObject("language", True)])
            description_languages.append(child.attrib["language"])
        elif child.tag == f"{NAMESPACE}data":
            logger.trace("Enter verify 'data' element")
            verify_attrib(child, [])
            if not isBase64(child.text):
                raise ElementError("Data value is not base 64", 0)
        verify_element(child, [])
        logger.success(f"'{child.tag[len(NAMESPACE):]}' element is valid")

    logger.trace("verifying 'description' element languages are unique")
    if len(description_languages) != len(set(description_languages)):
        logger.error("Each description element does not have a unique language")
        raise ElementError(
            "Each description element does not have a unique language", 0
        )
    logger.debug("'description' elements have unique languages")
    logger.success("'authenticationSuccess' element valid")


def validate_authenticationFailure(root: Element):
    allowed_elements = [
        ElementObject(f"{NAMESPACE}description", 0, None),
    ]
    logger.trace("Enter verify 'authenticationFailure' element")
    verify_element(root, allowed_elements)
    verify_attrib(root, [])
    description_languages = []
    for child in root:
        logger.trace("Enter verify 'description' element")
        verify_attrib(child, [AttribObject("language", True)])
        verify_element(child, [])
        description_languages.append(child.attrib["language"])
        logger.success("'description' element is valid")
    logger.trace("verify 'description' elements have unique language")
    if len(description_languages) != len(set(description_languages)):
        logger.error("Each 'description' element does not have a unique language")
        raise ElementError(
            "Each description element does not have a unique language", 0
        )
    logger.debug("Each 'description' element is unique")
    logger.success("'authenticationFailure' element is valid")


def validate_other(root: Element):
    allowed_elements = [
        ElementObject(f"{NAMESPACE}description", 0, None),
    ]
    logger.trace("Enter verify 'other' element")
    verify_element(root, allowed_elements)
    verify_attrib(root, [AttribObject("type", True)])
    description_languages = []
    for child in root:
        logger.trace("Enter verify 'description' element")
        verify_attrib(child, [AttribObject("language", True)])
        verify_element(child, [])
        description_languages.append(child.attrib["language"])
        logger.success("'description' element is valid")
    logger.trace("verify 'description' elements have unique language")
    if len(description_languages) != len(set(description_languages)):
        raise ElementError(
            "Each description element does not have a unique language", 0
        )
    logger.debug("Each 'description' element is unique")
    logger.success("'other' element is valid")


def validate_xml(file_name="unknown file"):
    logger.trace(f"Starting validation for file: {file_name}")
    try:
        file = ET.parse(file_name)
        root = file.getroot()
    except ET.ParseError as e:
        logger.error(f"XML parsing error in file {file_name}: {e}")
        return None
    except FileNotFoundError:
        logger.error(f"Error: File {file_name} not found")
        return None

    name = re.sub(r"\{.*?\}", "", root.tag)
    if name == "versions":
        try:
            validate_versions(root)
        except FileValidationError as e:
            logger.error(f"File {file_name} failed validation, Error: {e}")
            raise FileValidationError(file_name) from e

    elif name == "size":
        try:
            validate_size(root)
        except FileValidationError as e:
            logger.error(f"File {file_name} failed validation, Error: {e}")
            raise FileValidationError(file_name) from e

    elif name == "authenticationSuccess":
        try:
            validate_authenticationSuccess(root)
        except FileValidationError as e:
            logger.error(f"File {file_name} failed validation, Error: {e}")
            raise FileValidationError(file_name) from e

    elif name == "authenticationFailure":
        try:
            validate_authenticationFailure(root)
        except FileValidationError as e:
            logger.error(f"File {file_name} failed validation, Error: {e}")
            raise FileValidationError(file_name) from e

    elif name == "other":
        try:
            validate_other(root)
        except FileValidationError as e:
            logger.error(f"File {file_name} failed validation, Error: {e}")
            raise FileValidationError(file_name) from e

    else:
        logger.error(
            f"Root element '{root.tag[len(NAMESPACE):]}' is not IRIS conformant"
        )
        raise ElementError("Root element not IRIS conformant:", 2)
    logger.success("XML file validation completed successfully!")


validate_xml("/home/clark/repos/file-stream/tests/data/versions-example.xml")
