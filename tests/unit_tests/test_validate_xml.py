import pytest
from src.file_stream.validate_xml import verify_attrib
from src.file_stream.validate_xml import verify_element
from src.file_stream.validate_xml import validate_versions
from src.file_stream.validate_xml import verify_octetsType
from src.file_stream.validate_xml import validate_size

def test_verify_attrib(sample_root):
    allowed_attrib = ['id', 'name']
    element = sample_root.find('b')
    assert(verify_attrib(sample_root, allowed_attrib) == True)
    assert(verify_attrib(element, allowed_attrib) == False)

# def test_verify_element(sample_element):
#     pass

def test_validate_versions(valid_versions, invalid_versions):
    assert(validate_versions(valid_versions) == True)
    assert(validate_versions(invalid_versions) == False)

def test_verify_octetsType(valid_octets, invalid_octets):
    assert(verify_octetsType(valid_octets) == True)
    assert(verify_octetsType(invalid_octets) == False)

def test_validate_size(valid_size, invalid_size):
    assert(validate_size(valid_size) == True)
    assert(validate_size(invalid_size) == False)