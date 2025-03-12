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

@pytest.fixture
def valid_versions():
    xml_string = '''<?xml version="1.0" encoding="UTF-8"?>
                 <versions xmlns="urn:ietf:params:xml:ns:iris-transport">
                      <transferProtocol protocolId="iris.lwz"
                        authenticationIds="PLAIN EXTERNAL">
                        <application protocolId="urn:ietf:params:xml:ns:iris1"
                          extensionIds="http://example.com/SIMPLEBAG">
                          <dataModel protocolId="urn:ietf:params:xml:ns:dchk1"/>
                          <dataModel protocolId="urn:ietf:params:xml:ns:dreg1"/>
                        </application>
                      </transferProtocol>
                 </versions>
                 '''
    root = ET.fromstring(xml_string)
    return root

@pytest.fixture
def invalid_versions():
   xml_string = '''<?xml version="1.0" encoding="UTF-8"?>
                 <versions xmlns="urn:ietf:params:xml:ns:iris-transport">
                      <transferProtocol 
                        authenticationIds="PLAIN EXTERNAL">
                        <application protocolId="urn:ietf:params:xml:ns:iris1"
                          extensionIds="http://example.com/SIMPLEBAG">
                          <dataModel protocolId="urn:ietf:params:xml:ns:dchk1"/>
                          <dataModel protocolId="urn:ietf:params:xml:ns:dreg1"/>
                        </application>
                      </transferProtocol>
                 </versions>
                 '''
   root = ET.fromstring(xml_string)
   return root
