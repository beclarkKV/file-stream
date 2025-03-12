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


def verify_element(element: Element, required_tag: str, allowed_attrib: list) -> bool:
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


def verify_octetsType(element: Element) -> bool:
    exceeds = element.find('exceedsMaximum')
    octets = element.find('octets')
    if exceeds and octets is not None:
        return False
    if octets is not None:
        value = octets.text
        try:
            value = int(value)
            if value <= 0:
                return False
        except:
            return False
    return True


def validate_size(root: Element) -> bool:
    req_count=0
    res_count=0
    for child in root:
        name = re.sub(r'\{.*?\}', '', child.tag)
        if child.attrib != {}:
            return False
        if name == 'request':
            req_count += 1
        if name ==  'response':
            res_count += 1
        if not verify_octetsType(child):
            return False
    return req_count <= 1 and res_count <= 1
    



def validate_xml(xml: str) -> bool:
    file = ET.parse(xml)
    root = file.getroot()
    name = re.sub(r'\{.*?\}', '', root.tag)
    name = name.lower()
    if name == 'versions':
        return validate_versions(root)
    elif name == 'size':
        return validate_size(root)
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

print(validate_size(root))
        