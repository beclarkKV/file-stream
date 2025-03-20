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
from src.file_stream.validate_xml import verify_attrib
from src.file_stream.validate_xml import verify_element
from src.file_stream.validate_xml import verify_octetsType


def test_verify_attrib(sample_root):
    allowed_attrib = [AttribObject("id", 1), AttribObject("name", 1)]
    element = sample_root.find("b")
    element2 = sample_root.find("d")
    try:
        verify_attrib(sample_root, allowed_attrib, "sample.xml")

    except XMLAttributeError:
        pytest.fail("verify_attrib() raised XMLAttributeError unexpectedly")

    with pytest.raises(XMLAttributeError, match="Unexpected attributes found: "):
        verify_attrib(element, allowed_attrib, "sample.xml")
    with pytest.raises(XMLAttributeError, match="Missing required attribute:"):
        verify_attrib(element2, allowed_attrib, "sample.xml")


def test_verify_element(sample_root):
    allowed_elements = [
        ElementObject("b"),
        ElementObject("c", 0, 1),
        ElementObject("d"),
    ]
    element = sample_root.find("b")
    element1 = sample_root.find("c")
    with pytest.raises(ElementError, match="Too many occurences of element:"):
        verify_element(sample_root, allowed_elements, "sample.xml")
    with pytest.raises(ElementError, match="Missing required element:"):
        verify_element(element, allowed_elements, "sample.xml")
    with pytest.raises(ElementError, match="Unexpected elements found:"):
        verify_element(element1, allowed_elements, "sample.xml")


def test_validate_versions(valid_versions, invalid_versions):
    try:
        validate_versions(valid_versions, "sample.xml")
    except Exception as e:
        pytest.fail(f"validate_versions() raised and unexpected error Error: {e}")
    with pytest.raises(XMLAttributeError):
        validate_versions(invalid_versions, "sample.xml")


def test_validate_transferProtocol(valid_versions, invalid_versions):
    transfer_protocol_list = invalid_versions.findall(
        "{urn:ietf:params:xml:ns:iris-transport}transferProtocol"
    )
    with pytest.raises(XMLAttributeError, match="Missing required attribute:"):
        validate_transferProtocol(transfer_protocol_list[0], "sample.xml")

    with pytest.raises(XMLAttributeError, match="Unexpected attributes found:"):
        validate_transferProtocol(transfer_protocol_list[1], "sample.xml")

    with pytest.raises(ElementError, match="Unexpected elements found:"):
        validate_transferProtocol(transfer_protocol_list[2], "sample.xml")
    try:
        validate_transferProtocol(
            valid_versions.find(
                "{urn:ietf:params:xml:ns:iris-transport}transferProtocol"
            ),
            "sample.xml",
        )
    except Exception as e:
        pytest.fail(
            f"unexpected error came up with validate_transferProtocol Error: {e}"
        )


def test_validate_application(valid_versions, invalid_versions):
    transfer_protocol_list = invalid_versions.findall(
        "{urn:ietf:params:xml:ns:iris-transport}transferProtocol"
    )
    application_list = transfer_protocol_list[-1].findall(
        "{urn:ietf:params:xml:ns:iris-transport}application"
    )
    with pytest.raises(XMLAttributeError, match="Unexpected attributes found:"):
        validate_application(application_list[0], "sample.xml")
    with pytest.raises(XMLAttributeError, match="Missing required attribute:"):
        validate_application(application_list[1], "sample.xml")
    with pytest.raises(ElementError, match="Unexpected elements found:"):
        validate_application(application_list[2], "sample.xml")
    try:
        validate_application(
            valid_versions.find(
                "{urn:ietf:params:xml:ns:iris-transport}transferProtocol"
            ).find("{urn:ietf:params:xml:ns:iris-transport}application"),
            "sample.xml",
        )
    except Exception as e:
        pytest.fail(f"unexpected error came up with validate_application Error: {e}")


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
        validate_dataModel(data_model_list[1], "sample.xml")
    with pytest.raises(XMLAttributeError, match="Missing required attribute:"):
        validate_dataModel(data_model_list[0], "sample.xml")
    with pytest.raises(ElementError, match="Unexpected elements found:"):
        validate_dataModel(data_model_list[2], "sample.xml")
    try:
        validate_dataModel(
            valid_versions.find(
                "{urn:ietf:params:xml:ns:iris-transport}transferProtocol"
            )
            .find("{urn:ietf:params:xml:ns:iris-transport}application")
            .find("{urn:ietf:params:xml:ns:iris-transport}dataModel"),
            "sample.xml",
        )
    except Exception as e:
        pytest.fail(f"unexpected error came up with validate_dataModel Error: {e}")


def test_verify_octetsType(valid_size, invalid_size):
    with pytest.raises(
        ElementError, match="Cannot have octets value less than or equal to 0."
    ):
        verify_octetsType(
            invalid_size[0].find("{urn:ietf:params:xml:ns:iris-transport}response"),
            "sample.xml",
        )

    with pytest.raises(ElementError, match="octets value is not an integer."):
        verify_octetsType(
            invalid_size[1].find("{urn:ietf:params:xml:ns:iris-transport}response"),
            "sample.xml",
        )

    with pytest.raises(
        ElementError, match='Cannot have both "exceedsMaximum" and "octets" types'
    ):
        verify_octetsType(
            invalid_size[4].find("{urn:ietf:params:xml:ns:iris-transport}response"),
            "sample.xml",
        )

    try:
        verify_octetsType(
            valid_size.find("{urn:ietf:params:xml:ns:iris-transport}response"),
            "sample.xml",
        )
    except Exception as e:
        pytest.fail(f"verify_octets raised an unexpected error Error: {e}")


def test_validate_size(valid_size, invalid_size):
    with pytest.raises(
        ElementError, match="Cannot have octets value less than or equal to 0."
    ):
        validate_size(invalid_size[0], "sample.xml")

    with pytest.raises(ElementError, match="octets value is not an integer."):
        validate_size(invalid_size[1], "sample.xml")

    with pytest.raises(XMLAttributeError, match="Unexpected attributes found:"):
        validate_size(invalid_size[2], "sample.xml")

    with pytest.raises(ElementError, match="Unexpected elements found:"):
        validate_size(invalid_size[3], "sample.xml")

    with pytest.raises(
        ElementError, match='Cannot have both "exceedsMaximum" and "octets" types'
    ):
        validate_size(invalid_size[4], "sample.xml")

    with pytest.raises(XMLAttributeError, match="Unexpected attributes found:"):
        validate_size(invalid_size[5], "sample.xml")

    try:
        validate_size(valid_size, "sample.xml")
    except Exception as e:
        pytest.fail(f"unexpected error in validate_size Error: {e}")


def test_validate_authenticationSuccess(
    valid_authenticationSuccess, invalid_authenticationSuccess
):
    with pytest.raises(XMLAttributeError, match="Unexpected attributes found:"):
        validate_authenticationSuccess(invalid_authenticationSuccess[0], "sample.xml")
    with pytest.raises(XMLAttributeError, match="Unexpected attributes found:"):
        validate_authenticationSuccess(invalid_authenticationSuccess[1], "sample.xml")
    with pytest.raises(XMLAttributeError, match="Unexpected attributes found:"):
        validate_authenticationSuccess(invalid_authenticationSuccess[2], "sample.xml")
    with pytest.raises(ElementError, match="Unexpected elements found:"):
        validate_authenticationSuccess(invalid_authenticationSuccess[3], "sample.xml")
    with pytest.raises(ElementError, match="Unexpected elements found:"):
        validate_authenticationSuccess(invalid_authenticationSuccess[4], "sample.xml")
    with pytest.raises(
        ElementError, match="Each description element does not have a unique language"
    ):
        validate_authenticationSuccess(invalid_authenticationSuccess[5], "sample.xml")
    with pytest.raises(ElementError, match="Data value is not base 64"):
        validate_authenticationSuccess(invalid_authenticationSuccess[6], "sample.xml")
    with pytest.raises(XMLAttributeError, match="Missing required attribute:"):
        validate_authenticationSuccess(invalid_authenticationSuccess[7], "sample.xml")
    try:
        validate_authenticationSuccess(valid_authenticationSuccess, "sample.xml")
    except Exception as e:
        pytest.fail(f"unexpected error with validate_authenticationSuccess Error: {e}")


def test_validate_authenticationFailure(
    valid_authenticationFailure, invalid_authenticationFailure
):
    with pytest.raises(XMLAttributeError, match="Unexpected attributes found:"):
        validate_authenticationFailure(invalid_authenticationFailure[0], "sample.xml")
    with pytest.raises(XMLAttributeError, match="Unexpected attributes found:"):
        validate_authenticationFailure(invalid_authenticationFailure[1], "sample.xml")
    with pytest.raises(ElementError, match="Unexpected elements found:"):
        validate_authenticationFailure(invalid_authenticationFailure[2], "sample.xml")
    with pytest.raises(
        ElementError, match="Each description element does not have a unique language"
    ):
        validate_authenticationFailure(invalid_authenticationFailure[3], "sample.xml")
    with pytest.raises(ElementError, match="Unexpected elements found:"):
        validate_authenticationFailure(invalid_authenticationFailure[4], "sample.xml")
    with pytest.raises(XMLAttributeError, match="Missing required attribute:"):
        validate_authenticationFailure(invalid_authenticationFailure[5], "sample.xml")
    try:
        validate_authenticationFailure(valid_authenticationFailure, 'sample.xml')
    except Exception as e:
        pytest.fail(f'unexpected error with validate_authenticationFailure Error: {e}')