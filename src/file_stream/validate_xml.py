import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element
import re
from typing import List, Tuple, Optional, Dict, Set


class AttribObject:
    """
    Defines requirements for XML element attributes.
    
    Attributes:
        name: The name of the attribute
        amount_required: Minimum number of times this attribute must appear
        max_amount: Maximum number of times this attribute can appear (default: 1)
    """
    def __init__(self, name: str, amount_required: int = 1, max_amount: int = 1):
        if amount_required < 0:
            raise ValueError("amount_required cannot be negative")
        if max_amount < amount_required:
            raise ValueError("max_amount cannot be less than amount_required")
            
        self.name = name
        self.amount_required = amount_required
        self.max_amount = max_amount

    def __str__(self) -> str:
        return f"AttribObject(name='{self.name}', required={self.amount_required}, max={self.max_amount})"


def verify_attrib(element: Element, allowed_attrib: List[AttribObject]) -> Tuple[bool, Optional[str]]:
    """
    Verify that an element's attributes meet the requirements defined by AttribObjects.
    
    Args:
        element: The XML element to verify
        allowed_attrib: List of AttribObject defining attribute requirements
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Get all attribute names from the element
    element_attribs = set(element.attrib.keys())
    
    # Track which attributes we've validated
    validated_attribs = set()
    
    # Check each required attribute
    for attrib in allowed_attrib:
        count = element_attribs.count(attrib.name)
        validated_attribs.add(attrib.name)
        
        if count < attrib.amount_required:
            return False, f"Missing required attribute '{attrib.name}' (found {count}, required {attrib.amount_required})"
        if count > attrib.max_amount:
            return False, f"Too many occurrences of attribute '{attrib.name}' (found {count}, max {attrib.max_amount})"
    
    # Check for unexpected attributes
    unexpected = element_attribs - validated_attribs
    if unexpected:
        return False, f"Unexpected attributes found: {', '.join(unexpected)}"
    
    return True, None


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
    

def validate_authenticationSuccess(root: Element) -> bool:
    data_count = 0
    description_languages = []
    for child in root:
        if child.tag == '{urn:ietf:params:xml:ns:iris-transport}description' and child.attrib.keys() != {'language'}:
            return False
        
        elif child.tag == '{urn:ietf:params:xml:ns:iris-transport}data':
            data_count += 1
        
        description_languages.append(child.attrib['language'])
    
    if data_count > 1:
        return False
    
    if len(description_languages) != len(set(description_languages)):
        return False
    
    return True


def validate_authenticationFailure(root: Element) -> bool:
    description_languages = []
    for child in root:
        if child.tag == '{urn:ietf:params:xml:ns:iris-transport}description' and child.attrib.keys() != {'language'}:
            return False
        description_languages.append(child.attrib['language'])
    if len(description_languages) != len(set(description_languages)):
        return False
    return True


def validate_other(root: Element) -> bool:
    return validate_authenticationFailure(root)



def validate_xml(xml: str) -> bool:
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
    


