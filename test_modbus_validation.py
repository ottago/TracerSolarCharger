"""Frame validation tests for ModbusRTUClient, using a fake serial port."""
import struct

from tracer_solar_charger.modbus_client import ModbusRTUClient


class FakeSerial:
    """Serves queued response frames, one per request written."""

    is_open = True

    def __init__(self, responses):
        self.responses = list(responses)
        self.buf = b''

    def reset_input_buffer(self):
        self.buf = b''

    def write(self, data):
        self.buf = self.responses.pop(0) if self.responses else b''

    def read(self, n):
        out, self.buf = self.buf[:n], self.buf[n:]
        return out


def frame(slave, function, payload):
    body = struct.pack('>BB', slave, function) + payload
    return body + struct.pack('<H', ModbusRTUClient('x')._calculate_crc(body))


def read_resp(slave, values, function=4):
    return frame(slave, function, bytes([len(values) * 2]) + struct.pack('>%dH' % len(values), *values))


def client(responses):
    c = ModbusRTUClient('x', slave_id=1)
    c.serial_conn = FakeSerial(responses)
    return c


def test_valid_frame():
    assert client([read_resp(1, [1234])]).read_input_registers(0x3100, 1) == [1234]


def test_bad_crc_rejected():
    bad = bytearray(read_resp(1, [1234]))
    bad[-1] ^= 0xFF
    assert client([bytes(bad)] * 3).read_input_registers(0x3100, 1) is None


def test_wrong_slave_rejected():
    assert client([read_resp(3, [1234])] * 3).read_input_registers(0x3100, 1) is None


def test_exception_frame_rejected():
    assert client([frame(1, 0x84, bytes([2]))] * 3).read_input_registers(0x3100, 1) is None


def test_short_frame_rejected():
    assert client([read_resp(1, [1234])[:-3]] * 3).read_input_registers(0x3100, 1) is None


def test_wrong_register_count_rejected():
    assert client([read_resp(1, [1, 2])] * 3).read_input_registers(0x3100, 1) is None


def test_retry_recovers_from_corrupt_frame():
    bad = bytearray(read_resp(1, [77]))
    bad[3] ^= 0xFF
    assert client([bytes(bad), read_resp(1, [77])]).read_input_registers(0x3100, 1) == [77]


def test_combined_is_single_atomic_read():
    c = client([read_resp(1, [0x0002, 0x0001])])  # low word first, then high word
    assert c.read_combined_registers(0x3102, 0x3103) == 0x00010002
