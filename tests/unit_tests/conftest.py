"""Fixtures used in unit tests."""

import xml.etree.ElementTree as ET

import pytest


@pytest.fixture
def sample_root():
    xml_string = """<?xml version="1.0" encoding="UTF-8"?>
                     <a id="123" name="example">
                        <b id="nuts" name = "yes" wrong = "yes">
                          <d>text</d>
                        </b>
                        <c id ='123' name = "example">
                          <b>text</b>
                          <d>text</d>
                          <foo>text in foo</foo>
                        </c>
                        <c id='45' name='hello'>tect</c>
                        <d id="nuts">Some text inside d</d>
                     </a>"""
    root = ET.fromstring(xml_string)
    return root


@pytest.fixture
def valid_versions():
    xml_string = """<?xml version="1.0" encoding="UTF-8"?>
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
                 """
    root = ET.fromstring(xml_string)
    return root


@pytest.fixture
def invalid_versions():
    xml_string = """<?xml version="1.0" encoding="UTF-8"?>
<versions xmlns="urn:ietf:params:xml:ns:iris-transport">
     <transferProtocol authenticationIds="PLAIN EXTERNAL">
     </transferProtocol>

     <transferProtocol protocolId="iris.lwz" authenticaastionIds="PLAIN EXTERNAL">
     </transferProtocol>

     <transferProtocol protocolId="iris.lwz" authenticationIds="PLAIN EXTERNAL">
        <application protocolId="urn:ietf:params:xml:ns:iris1" extensaaionIds="http://example.com/SIMPLEBAG">
        </application>

        <application extensionIds="http://example.com/SIMPLEBAG">
        </application>

        <application protocolId="urn:ietf:params:xml:ns:iris1" extensionIds="http://example.com/SIMPLEBAG">
          <dataModel />
          <dataModel protocolId="urn:ietf:params:xml:ns:dchk1" message = 'hello'/>
          <dataModel protocolId="urn:ietf:params:xml:ns:dchk1"><note>this is a note</note></dataModel>
          <note>this is a note</note>
        </application>

        <note>this is a note</note>
     </transferProtocol>
</versions>
                 """
    root = ET.fromstring(xml_string)
    return root


@pytest.fixture
def valid_size():
    xml_string = """<?xml version="1.0" encoding="UTF-8"?>
   <size xmlns="urn:ietf:params:xml:ns:iris-transport">
     <response>
       <octets>1211</octets>
     </response>
   </size>"""
    root = ET.fromstring(xml_string)
    return root


@pytest.fixture
def invalid_size():
    xml_string = [
        """<?xml version="1.0" encoding="UTF-8"?>
                  <size xmlns="urn:ietf:params:xml:ns:iris-transport">
                   <response>
                     <octets>-1211</octets>
                   </response>
                  </size>
                  """,
        """<?xml version="1.0" encoding="UTF-8"?>
                  <size xmlns="urn:ietf:params:xml:ns:iris-transport">
                   <response>
                     <octets>rah</octets>
                   </response>
                  </size>
                  """,
        """<?xml version="1.0" encoding="UTF-8"?>
                  <size xmlns="urn:ietf:params:xml:ns:iris-transport">
                   <response invalid = 'True'>
                     <octets>1121</octets>
                   </response>
                  </size>
                  """,
        """<?xml version="1.0" encoding="UTF-8"?>
                  <size xmlns="urn:ietf:params:xml:ns:iris-transport">
                   <response>
                     <octets>1211</octets>
                     <note>text</note>
                   </response>
                  </size>
                  """,
        """<?xml version="1.0" encoding="UTF-8"?>
                  <size xmlns="urn:ietf:params:xml:ns:iris-transport">
                   <response>
                     <octets>1211</octets>
                     <exceedsMaximum/>
                   </response>
                  </size>
                  """,
        """<?xml version="1.0" encoding="UTF-8"?>
                  <size xmlns="urn:ietf:params:xml:ns:iris-transport">
                   <response>
                     <octets invalid = "True">1211</octets>
                   </response>
                  </size>
                  """,
    ]
    size_list = [ET.fromstring(i) for i in xml_string]
    return size_list


@pytest.fixture
def valid_authenticationSuccess():
    xml_string = """<?xml version="1.0" encoding="UTF-8"?>
<authenticationSuccess xmlns="urn:ietf:params:xml:ns:iris-transport">
    <description language="en">Authentication successful</description>
    <data>VGhpcyBpcyBhIHNhbXBsZSBkYXRhLg==</data>
</authenticationSuccess>"""
    root = ET.fromstring(xml_string)
    return root


@pytest.fixture
def invalid_authenticationSuccess():
    xml_string = [
        """<?xml version="1.0" encoding="UTF-8"?>
                <authenticationSuccess xmlns="urn:ietf:params:xml:ns:iris-transport" ID = 'yes'>
                    <description language="en">Authentication successful</description>
                    <data>VGhpcyBpcyBhIHNhbXBsZSBkYXRhLg==</data>
                </authenticationSuccess>""",
        """<?xml version="1.0" encoding="UTF-8"?>
                <authenticationSuccess xmlns="urn:ietf:params:xml:ns:iris-transport">
                    <description language="en" ID = 'yes'>Authentication successful</description>
                    <data>VGhpcyBpcyBhIHNhbXBsZSBkYXRhLg==</data>
                </authenticationSuccess>""",
        """<?xml version="1.0" encoding="UTF-8"?>
                <authenticationSuccess xmlns="urn:ietf:params:xml:ns:iris-transport">
                    <description language="en">Authentication successful</description>
                    <data ID='yes'>VGhpcyBpcyBhIHNhbXBsZSBkYXRhLg==</data>
                </authenticationSuccess>""",
        """<?xml version="1.0" encoding="UTF-8"?>
                <authenticationSuccess xmlns="urn:ietf:params:xml:ns:iris-transport">
                    <description language="en">Authentication successful</description>
                    <data>VGhpcyBpcyBhIHNhbXBsZSBkYXRhLg==</data>
                    <note>text</note>
                </authenticationSuccess>""",
        """<?xml version="1.0" encoding="UTF-8"?>
                <authenticationSuccess xmlns="urn:ietf:params:xml:ns:iris-transport">
                    <description language="en">
                      <note>text</note>
                    </description>
                    <data>VGhpcyBpcyBhIHNhbXBsZSBkYXRhLg==</data>
                </authenticationSuccess>""",
        """<?xml version="1.0" encoding="UTF-8"?>
                <authenticationSuccess xmlns="urn:ietf:params:xml:ns:iris-transport">
                    <description language="en">Success</description>
                    <description language="en">Success</description>
                    <data>VGhpcyBpcyBhIHNhbXBsZSBkYXRhLg==</data>
                </authenticationSuccess>""",
        """<?xml version="1.0" encoding="UTF-8"?>
                <authenticationSuccess xmlns="urn:ietf:params:xml:ns:iris-transport">
                    <description language="en">Success</description>
                    <data>fakl!!lkja</data>
                </authenticationSuccess>""",
        """<?xml version="1.0" encoding="UTF-8"?>
                <authenticationSuccess xmlns="urn:ietf:params:xml:ns:iris-transport">
                    <description>Authentication successful</description>
                    <data>VGhpcyBpcyBhIHNhbXBsZSBkYXRhLg==</data>
                </authenticationSuccess>""",
    ]
    auth_list = [ET.fromstring(i) for i in xml_string]
    return auth_list


@pytest.fixture
def valid_authenticationFailure():
    xml_string = """<?xml version="1.0" encoding="UTF-8"?>
<authenticationFailure xmlns="urn:ietf:params:xml:ns:iris-transport">
    <description language="en">Invalid credentials</description>
    <description language="fr">Identifiants invalides</description>
</authenticationFailure>"""
    root = ET.fromstring(xml_string)
    return root


@pytest.fixture
def invalid_authenticationFailure():
    xml_string = [
        """<?xml version="1.0" encoding="UTF-8"?>
                <authenticationFailure xmlns="urn:ietf:params:xml:ns:iris-transport" Id = '1'>
                    <description language="en">Invalid credentials</description>
                    <description language="fr">Identifiants invalides</description>
                </authenticationFailure>""",
        """<?xml version="1.0" encoding="UTF-8"?>
                <authenticationFailure xmlns="urn:ietf:params:xml:ns:iris-transport">
                    <description language="en" id ='1'>Invalid credentials</description>
                    <description language="fr">Identifiants invalides</description>
                </authenticationFailure>""",
        """<?xml version="1.0" encoding="UTF-8"?>
              <authenticationFailure xmlns="urn:ietf:params:xml:ns:iris-transport">
                  <description language="en">Invalid credentials</description>
                  <note language="fr">Identifiants invalides</note>
              </authenticationFailure>""",
        """<?xml version="1.0" encoding="UTF-8"?>
              <authenticationFailure xmlns="urn:ietf:params:xml:ns:iris-transport">
                  <description language="en">Invalid credentials</description>
                  <description language="en">Identifiants invalides</description>
              </authenticationFailure>""",
        """<?xml version="1.0" encoding="UTF-8"?>
              <authenticationFailure xmlns="urn:ietf:params:xml:ns:iris-transport">
                  <description language="en">
                    <not>text</not>
                  </description>
                  <description language="fr">Identifiants invalides</description>
              </authenticationFailure>""",
        """<?xml version="1.0" encoding="UTF-8"?>
              <authenticationFailure xmlns="urn:ietf:params:xml:ns:iris-transport">
                  <description>Invalid credentials</description>
                  <description language="fr">Identifiants invalides</description>
              </authenticationFailure>""",
    ]
    auth_list = [ET.fromstring(i) for i in xml_string]
    return auth_list
