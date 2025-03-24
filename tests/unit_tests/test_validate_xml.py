import pytest

from src.file_stream.validate_xml import AttribObject
from src.file_stream.validate_xml import ElementError
from src.file_stream.validate_xml import ElementObject
from src.file_stream.validate_xml import XMLAttributeError
from src.file_stream.validate_xml import validate_application
from src.file_stream.validate_xml import validate_authenticationFailure
from src.file_stream.validate_xml import validate_authenticationSuccess
from src.file_stream.validate_xml import validate_dataModel
from src.file_stream.validate_xml import validate_size
from src.file_stream.validate_xml import validate_transferProtocol
from src.file_stream.validate_xml import validate_versions
from src.file_stream.validate_xml import validate_xml
from src.file_stream.validate_xml import verify_attrib
from src.file_stream.validate_xml import verify_element
from src.file_stream.validate_xml import verify_octetsType


def test_verify_attrib(sample_root):
    allowed_attrib = [AttribObject("id", 1), AttribObject("name", 1)]
    element = sample_root.find("b")
    element2 = sample_root.find("d")
    verify_attrib(sample_root, allowed_attrib)

    with pytest.raises(XMLAttributeError, match="Unexpected attributes found: "):
        verify_attrib(element, allowed_attrib)
    with pytest.raises(XMLAttributeError, match="Missing required attribute:"):
        verify_attrib(element2, allowed_attrib)


def test_verify_element(sample_root):
    allowed_elements = [
        ElementObject("b"),
        ElementObject("c", 0, 1),
        ElementObject("d"),
    ]
    element = sample_root.find("b")
    element1 = sample_root.find("c")
    with pytest.raises(ElementError, match="Too many occurences of element:"):
        verify_element(sample_root, allowed_elements)
    with pytest.raises(ElementError, match="Missing required element:"):
        verify_element(element, allowed_elements)
    with pytest.raises(ElementError, match="Unexpected elements found:"):
        verify_element(element1, allowed_elements)


def test_validate_versions(valid_versions, invalid_versions):
    validate_versions(valid_versions)
    with pytest.raises(XMLAttributeError):
        validate_versions(invalid_versions)


def test_validate_transferProtocol(valid_versions, invalid_versions):
    transfer_protocol_list = invalid_versions.findall(
        "{urn:ietf:params:xml:ns:iris-transport}transferProtocol"
    )
    with pytest.raises(XMLAttributeError, match="Missing required attribute:"):
        validate_transferProtocol(transfer_protocol_list[0])

    with pytest.raises(XMLAttributeError, match="Unexpected attributes found:"):
        validate_transferProtocol(transfer_protocol_list[1])

    with pytest.raises(ElementError, match="Unexpected elements found:"):
        validate_transferProtocol(transfer_protocol_list[2])
    validate_transferProtocol(
        valid_versions.find("{urn:ietf:params:xml:ns:iris-transport}transferProtocol"),
    )


def test_validate_application(valid_versions, invalid_versions):
    transfer_protocol_list = invalid_versions.findall(
        "{urn:ietf:params:xml:ns:iris-transport}transferProtocol"
    )
    application_list = transfer_protocol_list[-1].findall(
        "{urn:ietf:params:xml:ns:iris-transport}application"
    )
    with pytest.raises(XMLAttributeError, match="Unexpected attributes found:"):
        validate_application(application_list[0])
    with pytest.raises(XMLAttributeError, match="Missing required attribute:"):
        validate_application(application_list[1])
    with pytest.raises(ElementError, match="Unexpected elements found:"):
        validate_application(application_list[2])
    validate_application(
        valid_versions.find(
            "{urn:ietf:params:xml:ns:iris-transport}transferProtocol"
        ).find("{urn:ietf:params:xml:ns:iris-transport}application"),
    )


def test_validate_dataModel(valid_versions, invalid_versions):
    transfer_protocol_list = invalid_versions.findall(
        "{urn:ietf:params:xml:ns:iris-transport}transferProtocol"
    )
    application_list = transfer_protocol_list[-1].findall(
        "{urn:ietf:params:xml:ns:iris-transport}application"
    )
    data_model_list = application_list[-1].findall(
        "{urn:ietf:params:xml:ns:iris-transport}dataModel"
    )
    with pytest.raises(XMLAttributeError, match="Unexpected attributes found:"):
        validate_dataModel(data_model_list[1])
    with pytest.raises(XMLAttributeError, match="Missing required attribute:"):
        validate_dataModel(data_model_list[0])
    with pytest.raises(ElementError, match="Unexpected elements found:"):
        validate_dataModel(data_model_list[2])
    validate_dataModel(
        valid_versions.find("{urn:ietf:params:xml:ns:iris-transport}transferProtocol")
        .find("{urn:ietf:params:xml:ns:iris-transport}application")
        .find("{urn:ietf:params:xml:ns:iris-transport}dataModel"),
    )


def test_verify_octetsType(valid_size, invalid_size):
    with pytest.raises(
        ElementError, match="Cannot have octets value less than or equal to 0."
    ):
        verify_octetsType(
            invalid_size[0].find("{urn:ietf:params:xml:ns:iris-transport}response"),
        )

    with pytest.raises(ElementError, match="octets value is not an integer."):
        verify_octetsType(
            invalid_size[1].find("{urn:ietf:params:xml:ns:iris-transport}response"),
        )

    with pytest.raises(
        ElementError, match='Cannot have both "exceedsMaximum" and "octets" types'
    ):
        verify_octetsType(
            invalid_size[4].find("{urn:ietf:params:xml:ns:iris-transport}response"),
        )

    verify_octetsType(
        valid_size.find("{urn:ietf:params:xml:ns:iris-transport}response"),
    )


def test_validate_size(valid_size, invalid_size):
    with pytest.raises(
        ElementError, match="Cannot have octets value less than or equal to 0."
    ):
        validate_size(invalid_size[0])

    with pytest.raises(ElementError, match="octets value is not an integer."):
        validate_size(invalid_size[1])

    with pytest.raises(XMLAttributeError, match="Unexpected attributes found:"):
        validate_size(invalid_size[2])

    with pytest.raises(ElementError, match="Unexpected elements found:"):
        validate_size(invalid_size[3])

    with pytest.raises(
        ElementError, match='Cannot have both "exceedsMaximum" and "octets" types'
    ):
        validate_size(invalid_size[4])

    with pytest.raises(XMLAttributeError, match="Unexpected attributes found:"):
        validate_size(invalid_size[5])

    validate_size(valid_size)


def test_validate_authenticationSuccess(
    valid_authenticationSuccess, invalid_authenticationSuccess
):
    with pytest.raises(XMLAttributeError, match="Unexpected attributes found:"):
        validate_authenticationSuccess(invalid_authenticationSuccess[0])
    with pytest.raises(XMLAttributeError, match="Unexpected attributes found:"):
        validate_authenticationSuccess(invalid_authenticationSuccess[1])
    with pytest.raises(XMLAttributeError, match="Unexpected attributes found:"):
        validate_authenticationSuccess(invalid_authenticationSuccess[2])
    with pytest.raises(ElementError, match="Unexpected elements found:"):
        validate_authenticationSuccess(invalid_authenticationSuccess[3])
    with pytest.raises(ElementError, match="Unexpected elements found:"):
        validate_authenticationSuccess(invalid_authenticationSuccess[4])
    with pytest.raises(
        ElementError, match="Each description element does not have a unique language"
    ):
        validate_authenticationSuccess(invalid_authenticationSuccess[5])
    with pytest.raises(ElementError, match="Data value is not base 64"):
        validate_authenticationSuccess(invalid_authenticationSuccess[6])
    with pytest.raises(XMLAttributeError, match="Missing required attribute:"):
        validate_authenticationSuccess(invalid_authenticationSuccess[7])
    validate_authenticationSuccess(valid_authenticationSuccess)


def test_validate_authenticationFailure(
    valid_authenticationFailure, invalid_authenticationFailure
):
    with pytest.raises(XMLAttributeError, match="Unexpected attributes found:"):
        validate_authenticationFailure(invalid_authenticationFailure[0])
    with pytest.raises(XMLAttributeError, match="Unexpected attributes found:"):
        validate_authenticationFailure(invalid_authenticationFailure[1])
    with pytest.raises(ElementError, match="Unexpected elements found:"):
        validate_authenticationFailure(invalid_authenticationFailure[2])
    with pytest.raises(
        ElementError, match="Each description element does not have a unique language"
    ):
        validate_authenticationFailure(invalid_authenticationFailure[3])
    with pytest.raises(ElementError, match="Unexpected elements found:"):
        validate_authenticationFailure(invalid_authenticationFailure[4])
    with pytest.raises(XMLAttributeError, match="Missing required attribute:"):
        validate_authenticationFailure(invalid_authenticationFailure[5])
    validate_authenticationFailure(valid_authenticationFailure)


def test_validate_xml():
    file_path = "/home/clark/repos/file-stream/FILES/"

    validate_xml(file_path + "versions-example.xml")
    validate_xml(file_path + "size-example.xml")
    validate_xml(file_path + "authenticationSuccess-example.xml")
    validate_xml(file_path + "authenticationFailure-example.xml")
    validate_xml(file_path + "other-example.xml")
