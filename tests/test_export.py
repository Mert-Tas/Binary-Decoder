import os
from binary_decoder import BinaryDecoder

def test_export(temp_path):
    decoder = BinaryDecoder("atrisense.bin")
    decoder.decode_records()
    decoder.convert_angles()

    output_file = temp_path / "test_output.ply"
    decoder.export_to_ply(output_file)

    assert os.path.exists(output_file)
    assert os.path.getsize(output_file) > 0