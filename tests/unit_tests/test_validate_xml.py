import pytest
from src.file_stream.validate_xml import verify_attrib

def test_verify_attrib(sample_root):
    allowed_attrib = ['id', 'name']
    element = sample_root.find('b')
    assert(verify_attrib(sample_root, allowed_attrib) == True)
    assert(verify_attrib(element, allowed_attrib) == False)