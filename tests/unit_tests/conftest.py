"""Fixtures used in unit tests."""
import pytest
import xml.etree.ElementTree as ET
@pytest.fixture
def sample_root():
    xml_string =  """<?xml version="1.0" encoding="UTF-8"?>
                     <a id="123" name="example">
                        <b id="nuts" name = "yes" wrong = "yes">Some text inside b</b>
                        <b id="nuts" name = "yes" wrong = "yes">Some text inside b</b>
                        <b id="nuts" name = "yes" wrong = "yes">Some text inside b</b>
                     </a>"""
    root = ET.fromstring(xml_string)
    return root 

