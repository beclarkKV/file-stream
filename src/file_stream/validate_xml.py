import base64
from dataclasses import dataclass
from typing import List

from loguru import logger
from lxml import etree as ET
from lxml.etree import Element

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


def get_line_number(element: Element) -> int:
    return element.sourceline if hasattr(element, "sourceline") else 0


def isBase64(s):
    try:
        return base64.b64encode(base64.b64decode(s)).decode() == s
    except:
        return False


def verify_attrib(element: Element, allowed_attrib: List[AttribObject]):
    logger.trace("verifying correct attributes")
    keys = set(element.keys())
    allowed_names = {attrib.name for attrib in allowed_attrib}
    check_required_attrib(allowed_attrib, keys, element)
    invalid_attrib = keys - allowed_names
    if invalid_attrib != set():
        raise XMLAttributeError(
            f"Unexpected attributes found: {invalid_attrib}", get_line_number(element)
        )
    logger.debug("attributes valid")


def check_required_attrib(
    allowed_attrib: List[AttribObject], actual_attrib: set, element: Element
) -> list:
    required_attrib = {attrib.name for attrib in allowed_attrib if attrib.required}
    if required_attrib - actual_attrib != set():
        raise XMLAttributeError(
            f"Missing required attribute: {required_attrib}.", get_line_number(element)
        )


def verify_element(element: Element, required_elements: List[ElementObject]):
    logger.trace("verifying correct children")
    for child in required_elements:
        element_list = element.findall(child.name)
        count = len(element_list)
        if (child.max_occur is not None) and (count > child.max_occur):
            raise ElementError(
                f"Too many occurences of element: {child.name}.(found: {count} max: {child.max_occur})",
                get_line_number(element),
            )
        if count < child.min_occur:
            raise ElementError(
                f"Missing required element: {child.name}. (found: {count}, required: {child.min_occur})",
                get_line_number(element),
            )
    expected_elements = {child.name for child in required_elements}
    actual_elements = {child.tag for child in element}
    if actual_elements - expected_elements != set():
        raise ElementError(
            f"Unexpected elements found: {actual_elements - expected_elements}",
            get_line_number(element),
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
        raise ElementError(
            'Cannot have both "exceedsMaximum" and "octets" types',
            get_line_number(element),
        )
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
    verify_descriptions_element(root)
    for child in root.findall(f"{NAMESPACE}data"):
        logger.trace("Enter verify 'data' element")
        verify_attrib(child, [])
        if not isBase64(child.text):
            raise ElementError("Data value is not base 64", get_line_number(child))
        verify_element(child, [])
        logger.success(f"'{child.tag[len(NAMESPACE):]}' element is valid")

    logger.success("'authenticationSuccess' element valid")


def validate_authenticationFailure(root: Element):
    allowed_elements = [
        ElementObject(f"{NAMESPACE}description", 0, None),
    ]
    logger.trace("Enter verify 'authenticationFailure' element")
    verify_element(root, allowed_elements)
    verify_attrib(root, [])
    verify_descriptions_element(root)
    logger.success("'authenticationFailure' element is valid")


def validate_other(root: Element):
    allowed_elements = [
        ElementObject(f"{NAMESPACE}description", 0, None),
    ]
    logger.trace("Enter verify 'other' element")
    verify_element(root, allowed_elements)
    verify_attrib(root, [AttribObject("type", True)])
    verify_descriptions_element(root)
    logger.success("'other' element is valid")


def verify_descriptions_element(root: Element):
    description_languages = []
    for child in root.findall(f"{NAMESPACE}description"):
        logger.trace("Enter verify 'description' element")
        verify_attrib(child, [AttribObject("language", True)])
        description_languages.append(child.attrib["language"])
        verify_element(child, [])
        logger.success(f"'{child.tag[len(NAMESPACE):]}' element is valid")
    logger.trace("verifying 'description' element languages are unique")
    if len(description_languages) != len(set(description_languages)):
        logger.error("Each description element does not have a unique language")
        raise ElementError(
            "Each description element does not have a unique language",
            get_line_number(root),
        )
    logger.debug("'description' elements have unique languages")


def validate_xml(file_name="unknown file"):
    logger.trace(f"Starting validation for file: {file_name}")
    try:
        file = ET.parse(file_name)
        root = file.getroot()
    except ET.ParseError as e:
        logger.error(f"XML parsing error in file {file_name}: {e}")
        raise FileValidationError(file_name) from e
    except FileNotFoundError as e:
        logger.error(f"Error: File {file_name} not found")
        raise FileValidationError(file_name) from e

    validation_functions = {
        "versions": validate_versions,
        "size": validate_size,
        "authenticationSuccess": validate_authenticationSuccess,
        "authenticationFailure": validate_authenticationFailure,
        "other": validate_other,
    }

    name = root.tag[len(NAMESPACE) :]

    if name not in validation_functions.keys():
        logger.error(
            f"Root element '{root.tag[len(NAMESPACE):]}' is not IRIS conformant"
        )
        raise ElementError("Root element not IRIS conformant:", get_line_number(root))
    try:
        validation_functions[name](root)
    except FileValidationError as e:
        logger.error(f"File {file_name} failed validation, Error: {e}")
        raise FileValidationError(file_name) from e

    logger.success("XML file validation completed successfully!")
