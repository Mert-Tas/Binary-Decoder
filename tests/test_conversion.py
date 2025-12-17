import numpy as np
from pathlib import Path 
from binary_decoder import BinaryDecoder

DATA_FILE = Path(__file__).resolve().parents[1] / "binary_decoder" / "atrisense.bin"

# Mathematical correctness test
def test_cartesian_conversion():
    decoder = BinaryDecoder(str(DATA_FILE))
    decoder.read_binary()
    decoder.decode_records()
    decoder.convert_angles()

    x, y, z, _ = decoder.cartesian_points[0]
    _, _, _, distance, _ = decoder.records[0]

    reconstructed = np.sqrt(x*x + y*y + z*z)
    assert np.isclose(reconstructed, distance, rtol=1e-5)
