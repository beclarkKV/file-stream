import pytest
from src.file_stream.validate_xml import verify_attrib
from src.file_stream.validate_xml import verify_children

def test_verify_attrib(sample_root):
    allowed_attrib = ['id', 'name']
    element = sample_root.find('b')
    assert(verify_attrib(sample_root, allowed_attrib) == True)
    assert(verify_attrib(element, allowed_attrib) == False)

def test_children(sample_root):
    required_tag = 'b'
    assert(verify_children(sample_root, required_tag) == True)