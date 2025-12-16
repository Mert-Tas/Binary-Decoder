import os
# binary_decoder is the package name 
from binary_decoder import BinaryDecoder

def test_export(tmp_path):
    # NOTE: tmp_path is a fşxture name !
    decoder = BinaryDecoder("atrisense.bin")
    decoder.decode_records()
    decoder.convert_angles()

    output_file = tmp_path / "test_output.ply"
    decoder.export_to_ply(output_file)

    assert os.path.exists(output_file)
    assert os.path.getsize(output_file) > 0