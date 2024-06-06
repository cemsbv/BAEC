import pytest

from baec.measurements.measurement_device import MeasurementDevice


def test_measurement_device_with_valid_input() -> None:
    """Test initialization of MeasurementDevice with valid input."""
    # With QR code
    device = MeasurementDevice(id_="device_1", qr_code="qr_code_1")
    assert device.id == "device_1"
    assert device.qr_code == "qr_code_1"

    # Without QR code
    device = MeasurementDevice(id_="device_1")
    assert device.id == "device_1"
    assert device.qr_code is None


def test_measurement_device_init_with_invalid_id() -> None:
    """Test initialization of MeasurementDevice with invalid ID."""
    # Invalid id: None
    with pytest.raises(TypeError, match="id"):
        MeasurementDevice(id_=None)

    # Invalid id: Empty string
    with pytest.raises(ValueError, match="id"):
        MeasurementDevice(id_="")


def test_measurement_device_init_with_invalid_qr_code() -> None:
    """Test initialization of MeasurementDevice with invalid QR-code."""
    # Invalid id: Integer value
    with pytest.raises(TypeError, match="qr_code"):
        MeasurementDevice(id_="device_1", qr_code=1)

    # Invalid id: Empty string
    with pytest.raises(ValueError, match="qr_code"):
        MeasurementDevice(id_="device_1", qr_code="")


def test_measurement_device__eq__method() -> None:
    """Test the __eq__ method of MeasurementDevice."""
    device_1 = MeasurementDevice(id_="device_1", qr_code="qr_code_1")
    device_2 = MeasurementDevice(id_="device_1", qr_code="qr_code_1")
    device_3 = MeasurementDevice(id_="device_2", qr_code="qr_code_2")
    device_4 = MeasurementDevice(id_="device_2", qr_code="qr_code_1")

    assert device_1 == device_2
    assert device_1 != device_3
    assert device_1 != device_4
    assert device_2 != device_3
    assert device_3 == device_4

    assert device_1 == device_1
    assert device_1 != "device_1"
