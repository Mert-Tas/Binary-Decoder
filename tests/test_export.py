import os
from pathlib import Path
# binary_decoder is the package name 
from binary_decoder import BinaryDecoder

DATA_FILE = Path(__file__).resolve().parents[1] / "binary_decoder" / "atrisense.bin"

def test_export(tmp_path):
    # NOTE: tmp_path is a fixture name !
    decoder = BinaryDecoder(str(DATA_FILE))
    decoder.read_binary()
    decoder.decode_records()
    decoder.convert_angles()

    output_file = tmp_path / "test_output.ply"
    decoder.export_to_ply(output_file)

    assert os.path.exists(output_file)
    assert os.path.getsize(output_file) > 0