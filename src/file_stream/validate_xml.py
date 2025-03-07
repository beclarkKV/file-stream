import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element

def validate_versions(root: Element) -> bool:
    pass

def validate_transferProtocol(transferProtocol: Element) -> bool:
    pass

def validate_application(application: Element) -> bool:
    pass

def verify_attrib(element: Element, allowed_attrib: list) -> bool:
    for attrib in element.attrib.keys():
        if attrib not in allowed_attrib:
            return False
    return True
