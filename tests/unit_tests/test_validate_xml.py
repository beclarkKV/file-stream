import pytest
from src.file_stream.validate_xml import AttribObject   
from src.file_stream.validate_xml import ElementObject
from src.file_stream.validate_xml import verify_attrib
from src.file_stream.validate_xml import verify_element
from src.file_stream.validate_xml import validate_versions
from src.file_stream.validate_xml import verify_octetsType
from src.file_stream.validate_xml import validate_size

def test_verify_attrib(sample_root):
    allowed_attrib = [AttribObject('id', 1), AttribObject('name', 1)]
    element = sample_root.find('b')
    element1 = sample_root.find('c')
    element2 = sample_root.find('d')
    assert(verify_attrib(sample_root, allowed_attrib) == (True, "None"))
    assert(verify_attrib(element, allowed_attrib) == (False, 'Unexpected attributes found: {\'wrong\'}'))
    assert(verify_attrib(element2, allowed_attrib) == (False, 'Missing required attribute: name.'))

# def test_verify_element(sample_element):
#     pass

def test_validate_versions(valid_versions, invalid_versions):
    assert(validate_versions(valid_versions) == (True, 'None'))
    assert(validate_versions(invalid_versions) == (False, 'Missing required attribute: protocolId.'))

def test_verify_octetsType(valid_octets, invalid_octets):
    assert(verify_octetsType(valid_octets) == (True, 'None'))
    assert(verify_octetsType(invalid_octets) == (False, 'Cannot have octets value less than or equal to 0.  Value: -5000'))

def test_validate_size(valid_size, invalid_size):
    assert(validate_size(valid_size) == (True, 'None'))
    assert(validate_size(invalid_size) == (False, "Unexpected attributes found: {'invalid'}"))