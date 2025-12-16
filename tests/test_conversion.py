import numpy as np
from binary_decoder import BinaryDecoder

# Mathematical correctness test
def test_cartesian_conversion():
    decoder = BinaryDecoder("../atrisense.bin")
    decoder.read_binary()
    decoder.decode_records()
    decoder.convert_angles()

    x, y, z, _ = decoder.cartesian_points[0]
    _, _, _, distance, _ = decoder.records[0]

    reconstructed = np.sqrt(x*x + y*y + z*z)
    assert np.isclose(reconstructed, distance, rtol=1e-5)
