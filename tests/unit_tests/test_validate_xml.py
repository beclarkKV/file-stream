import pytest
from src.file_stream.validate_xml import verify_attrib
from src.file_stream.validate_xml import validate_versions

def test_verify_attrib(sample_root):
    allowed_attrib = ['id', 'name']
    element = sample_root.find('b')
    assert(verify_attrib(sample_root, allowed_attrib) == True)
    assert(verify_attrib(element, allowed_attrib) == False)

def test_validate_versions(valid_versions, invalid_versions):
    assert(validate_versions(valid_versions) == True)
    assert(validate_versions(invalid_versions) == False)