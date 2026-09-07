"""Small protobuf message implementation for the greeting example.

Run ``python -m grpc_tools.protoc`` to regenerate this module in a project
that uses a locally installed protobuf compiler.
"""


def _encode_string(field_number: int, value: str) -> bytes:
    encoded = value.encode("utf-8")
    length = len(encoded)
    length_bytes = bytearray()
    while length > 0x7F:
        length_bytes.append((length & 0x7F) | 0x80)
        length >>= 7
    length_bytes.append(length)
    return bytes((field_number << 3 | 2,)) + bytes(length_bytes) + encoded


def _decode_string(data: bytes) -> str:
    if not data or data[0] != 0x0A:
        raise ValueError("invalid protobuf string field")
    length = data[1]
    offset = 2
    if length & 0x80:
        length = length & 0x7F
        shift = 7
        while True:
            byte = data[offset]
            offset += 1
            length |= (byte & 0x7F) << shift
            if not byte & 0x80:
                break
            shift += 7
    return data[offset : offset + length].decode("utf-8")


class HelloRequest:
    def __init__(self, name: str = ""):
        self.name = name

    def SerializeToString(self) -> bytes:
        return _encode_string(1, self.name) if self.name else b""

    @classmethod
    def FromString(cls, data: bytes):
        if not data:
            return cls()
        return cls(_decode_string(data))


class HelloReply:
    def __init__(self, message: str = ""):
        self.message = message

    def SerializeToString(self) -> bytes:
        return _encode_string(1, self.message) if self.message else b""

    @classmethod
    def FromString(cls, data: bytes):
        if not data:
            return cls()
        return cls(_decode_string(data))
