from binary_decoder import BinaryDecoder

def test_decode_binary():
    decoder = BinaryDecoder("atrisense.bin")
    decoder.read_binary()
    records = decoder.decode_records()

    assert len(records) > 0
    scan, x_ang, y_ang, dist, intensity = records[0]

    assert isinstance(scan, int)
    assert isinstance(x_ang, float)
    assert isinstance(y_ang, float)
    assert dist > 0
    assert intensity >= 0
