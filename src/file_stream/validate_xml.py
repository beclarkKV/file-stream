import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element

def validate_versions(root: Element) -> bool:
    pass

def validate_transferProtocol(transferProtocol: Element) -> bool:
    allowed_attrib = ['protocolIds', 'extensionIds', 'authenticationIds', 'responseSizeOctets', 'requestSizeOctets']
    if not verify_attrib(transferProtocol, allowed_attrib):
        return False

def validate_application(application: Element) -> bool:
    allowed_attrib = ['protocolIds', 'extensionIds']
    if not verify_attrib(application, allowed_attrib):
        return False
    
    return True
    
def validate_dataModel(dataModel: Element):
    allowed_attrib = ['protocolIds', 'extensionIds']
    if not verify_attrib(dataModel, allowed_attrib):
        return False
    return True
    
def verify_attrib(element: Element, allowed_attrib: list) -> bool:
    if allowed_attrib[0] not in element.attrib.keys():
        return False
    for attrib in element.attrib.keys():
        if attrib not in allowed_attrib:
            return False
    return True

def verify_children(element: Element, required_tag: str):
    for child in element:
        if child.tag != required_tag:
            return False
    return True