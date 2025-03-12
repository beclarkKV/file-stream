import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element
import re



def verify_attrib(element: Element, allowed_attrib: list) -> bool:
    if allowed_attrib[0] not in element.attrib.keys():
        return False
    for attrib in element.attrib.keys():
        if attrib not in allowed_attrib:
            return False
    return True

def verify_element(element: Element, required_tag: str, allowed_attrib: list):
    if element.tag != required_tag:
        return False
    return verify_attrib(element, allowed_attrib)



def validate_versions(root: Element) -> bool:
    allowed_attrib = {
                      'transferProtocol': ['protocolId', 'extensionIds', 'authenticationIds', 'responseSizeOctets', 'requestSizeOctets'], 
                      'application': ['protocolId', 'extensionIds'],
                      'dataModel': ['protocolId', 'extensionIds']}
    
    for transferprotocol in root:
        if not verify_element(transferprotocol, '{urn:ietf:params:xml:ns:iris-transport}transferProtocol', allowed_attrib['transferProtocol']):
            return False
        for application in transferprotocol:
            if not verify_element(application, '{urn:ietf:params:xml:ns:iris-transport}application', allowed_attrib['application']):
                return False
            for dataModel in application:
                if not verify_element(dataModel, '{urn:ietf:params:xml:ns:iris-transport}dataModel', allowed_attrib['dataModel']):
                    return False
    return True

def validate_xml(xml: str) -> bool:
    file = ET.parse(xml)
    root = file.getroot()
    name = cleaned_text = re.sub(r'\{.*?\}', '', root.tag)
    name = name.lower()
    if name == 'versions':
        return validate_versions(root)
    elif name == 'size':
        pass
    elif name == 'authenticationSuccess':
        pass
    elif name == 'authenticationFailure':
        pass
    elif name == 'other':
        pass
    else:
        pass
    


xml = ET.parse('fixable.xml')
root = xml.getroot()

print(validate_xml('valid.xml'))
        