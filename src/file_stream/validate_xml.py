import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element
import re
from typing import List, Tuple

class AttribObject():
    def __init__(self, name: str, required = False):
        self.name = name
        self.required = required
        
def verify_attrib(element: Element, allowed_attrib: List[AttribObject]) -> Tuple[bool, str]:
    keys = element.keys()
    validated_attrib = set()
    for attrib in allowed_attrib:
        count = keys.count(attrib.name)
        validated_attrib.add(attrib.name)
        if count < 1 and attrib.required:
            return (False, f'Missing required attribute: {attrib.name}.')
        if count > 1:
            return (False, f'Too many occurences of attribute: {attrib.name}. (found {count})')
    invalid_attrib = set(keys) - validated_attrib
    if invalid_attrib != set():
        return (False, f'Unexpected attributes found: {invalid_attrib}')
    return (True, 'None')

class ElementObject:
    def __init__(self, name: str, min_occur = 1, max_occur = 1):
        self.name = name
        self.min_occur = min_occur
        self.max_occur = max_occur

def verify_element(element: Element, required_elements: List[ElementObject]) -> Tuple[bool, str]:
    for child in required_elements:
        element_list = element.findall(child.name)
        count = len(element_list)
        if (child.max_occur is not None) and (count > child.max_occur):
            return (False, f'Too many occurences of element: {child.name}.(found: {count} max: {child.max_occur})')
        if count < child.min_occur:
            return (False, f'Missing required element: {child.name}. (found: {count}, required: {child.min_occur})')
    expected_elements = {child.name for child in required_elements}
    actual_elements = {child.tag for child in element}

    if actual_elements - expected_elements != set():
        return (False, f'Unexpected elements found: {actual_elements}')
    
    return (True, 'None')

        
def validate_versions(root: Element) -> Tuple[bool, str]:
    allowed_attrib = {
        'transferProtocol': [AttribObject('protocolId', True), AttribObject('extensionIds'), AttribObject('authenticationIds'), AttribObject('responseSizeOctets'), AttribObject('requestSizeOctets')], 
        'application': [AttribObject('protocolId', True), AttribObject('extensionIds')],
        'dataModel': [AttribObject('protocolId', True), AttribObject('extensionIds')]
    }
    
    result = verify_element(root, [ElementObject('{urn:ietf:params:xml:ns:iris-transport}transferProtocol', 1, None)])
    if not result[0]:
        return result
    
    
    for transferprotocol in root:
        result = verify_element(transferprotocol, [ElementObject('{urn:ietf:params:xml:ns:iris-transport}application', 0, None)])
        if not result[0]:
            return result
        
        result = verify_attrib(transferprotocol, allowed_attrib['transferProtocol'])
        if not result[0]:
            return result
        
        for application in transferprotocol:
            result = verify_element(application, [ElementObject('{urn:ietf:params:xml:ns:iris-transport}dataModel', 0, None)])
            if not result[0]:
                return result
            
            result = verify_attrib(application, allowed_attrib['application'])
            if not result[0]:
                return result
            
            for datamodel in application:
                result = verify_attrib(datamodel, allowed_attrib['dataModel'])
                if not result[0]:
                    return result 
    return (True, 'None')


def verify_octetsType(element: Element) -> Tuple[bool, str]:
    exceeds = element.find('exceedsMaximum')
    octets = element.find('octets')
    if exceeds and octets is not None:
        return (False, 'Cannot have both "exceedsMaximum" and "octets" types')
    if octets is not None:
        value = octets.text
        try:
            value = int(value)
            if value <= 0:
                return (False, f'Cannot have octets value less than or equal to 0.  Value: {value}')
        except:
            return (False, f'octets value is not an integer.  Value: {value}')
    return (True, 'None')


def validate_size(root: Element) -> Tuple[bool, str]:
    req_count=0
    res_count=0
    allowed_elements = [ElementObject('{urn:ietf:params:xml:ns:iris-transport}request', 0, 1), ElementObject('{urn:ietf:params:xml:ns:iris-transport}response', 0, 1)]
    
    result  = verify_element(root, allowed_elements)
    if not result[0]:
        return result
    
    result = verify_attrib(root, [])
    if not result[0]:
        return result
    
    for child in root:
        result = verify_attrib(child, [])
        if not result[0]:
            return result
        
        result = verify_octetsType(child)
        if not result[0]:
            return result
        
    return (True, 'None')
    

def validate_authenticationSuccess(root: Element) -> Tuple[bool, str]:
    data_count = 0
    description_languages = []
    for child in root:
        if child.tag != '{urn:ietf:params:xml:ns:iris-transport}description' and child.attrib.keys() != {'language'}:
            return False
        
        elif child.tag == '{urn:ietf:params:xml:ns:iris-transport}data':
            data_count += 1
        
        description_languages.append(child.attrib['language'])
    
    if data_count > 1:
        return False
    
    if len(description_languages) != len(set(description_languages)):
        return False
    
    return True


def validate_authenticationFailure(root: Element) -> Tuple[bool, str]:
    description_languages = []
    for child in root:
        if child.tag == '{urn:ietf:params:xml:ns:iris-transport}description' and child.attrib.keys() != {'language'}:
            return False
        description_languages.append(child.attrib['language'])
    if len(description_languages) != len(set(description_languages)):
        return False
    return True


def validate_other(root: Element) -> Tuple[bool, str]:
    return validate_authenticationFailure(root)



def validate_xml(xml: str) -> Tuple[bool, str]:
    try:
        file = ET.parse(xml)
        root = file.getroot()
    except ET.ParseError as e:
        print(f'XML parsing error: {e}')
        return False
    except FileNotFoundError:
        print('Error: File not found')
        return False
    
    name = re.sub(r'\{.*?\}', '', root.tag)
    if name == 'versions':
        return validate_versions(root)
    
    elif name == 'size':
        return validate_size(root)
    
    elif name == 'authenticationSuccess':
        return validate_authenticationSuccess(root)
    
    elif name == 'authenticationFailure':
        return validate_authenticationFailure(root)
    
    elif name == 'other':
        return validate_other(root)
    
    else:
        raise('not a iris conformant xml')
    

