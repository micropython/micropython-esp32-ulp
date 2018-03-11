from esp32_ulp.link import make_binary


def test_make_binary():
    text = b'\x12\x34\x56\x78'
    data = b'\x11\x22\x33\x44'
    bss_size = 40
    bin = make_binary(text, data, bss_size)
    assert len(bin) == 12 + len(text) + len(data)
    assert bin.startswith(b'\x75\x6c\x70\x00')  # magic, LE
    assert bin.endswith(text+data)


test_make_binary()

