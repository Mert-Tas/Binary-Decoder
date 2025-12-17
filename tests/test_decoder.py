from pathlib import Path
from binary_decoder import BinaryDecoder

# __file__ is actual location of the test file, parents[1] is repo root
DATA_FILE = Path(__file__).resolve().parents[1] / "binary_decoder" / "atrisense.bin"

def test_decode_binary():
    decoder = BinaryDecoder(str(DATA_FILE))
    decoder.read_binary()
    decoder.decode_records()

    assert len(decoder.records) > 0
    scan, x_ang, y_ang, dist, intensity = decoder.records[0]

    assert isinstance(scan, int)
    assert isinstance(x_ang, float)
    assert isinstance(y_ang, float)
    assert dist > 0
    assert intensity >= 0
