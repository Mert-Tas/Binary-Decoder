
#!/usr/bin/python

import os
import sys
import struct
import numpy as np

class BinaryDecoder:

    def __init__(self, binFile : str):
        self.binFile = binFile
        self.fileLen = 0
        self.rawData = b""
        # Stores all individual records
        self.records = []
        # Stores the converted cartesian points and intensity
        self.cartesian_points = []

    def read_binary(self):
        with open(self.binFile, "rb") as f:
            self.rawData = f.read()

        self.fileLen = len(self.rawData)
        if self.fileLen == 0:
            raise ValueError("Binary file is empty.")

        print(f"Read {self.fileLen} bytes from {self.binFile}")

    """
    Defines the struct format for a record:
    struct AtrisenseRecord {
        uint32_t scan_number;  -> I  4 bytes
        float    x_angle_deg;  -> f  4 bytes
        float    y_angle_deg;  -> f  4 bytes
        float    distance_m;   -> f  4 bytes
        uint16_t intensity;    -> H  2 bytes
    };
    Struct format ("<IfffH") uses little-endian (<)
    Total record size = 18 bytes 
    """
    def decode_records(self):
        if not self.rawData:
            raise RuntimeError("No raw data loaded. Call read_binary() first")

        atrisense_record = struct.Struct("<IfffH")
        record_size = atrisense_record.size  # 18 bytes

        if len(self.rawData) % record_size != 0:
            raise ValueError("Binary file size is not aligned with record size.")

        # Each record is in the format:
        # (scan_number, x_angle_deg, y_angle_deg, distance_m, intensity)
        for i in range (0, self.fileLen, record_size):
            chunk = self.rawData[i : i + record_size]
            record = atrisense_record.unpack(chunk)
            self.records.append(record)

        print(f"Decoded {len(self.records)} records successfully")
            
    def convert_angles(self):
        if not hasattr(self, "records") or len(self.records) == 0:
            raise RuntimeError("No decoded records found. Call decode_records() first")

        for rec in self.records:
            scan_number, x_angle_deg, y_angle_deg, distance_m, intensity = rec

            if distance_m <= 0:
                continue

            # Convert degrees to radians
            x_rad = np.deg2rad(x_angle_deg)
            y_rad = np.deg2rad(y_angle_deg)

            # Calculate cartesian coordinates
            x = distance_m * np.cos(y_rad) * np.cos(x_rad)
            y = distance_m * np.cos(y_rad) * np.sin(x_rad)
            z = distance_m * np.sin(y_rad)

            self.cartesian_points.append((x, y, z, intensity))
        
        print(f"Converted {len(self.cartesian_points)} records to Cartesian coordinates")

    def validate_cartesian_points(self):
        if not hasattr(self, "cartesian_points") or len(self.cartesian_points) == 0:
            raise RuntimeError("No Cartesian points available. Run convert_angles() first.")

    """
    Verifies a set of cartesian points by comparing them
    to the distance from a given index in the point list.
    sqrt(x² + y² + z²) ≈ distance_m
    """
    def verify_distance(self, index, tolerance = 1e-4):
        x, y, z, _ = self.cartesian_points[index]
        _, _, _, distance, _ = self.records[index]

        computed_distance = (x**2 + y**2 + z**2)
        # Use tolerance-based comparison due to floating-point precision
        return abs(computed_distance - distance**2) < tolerance
    
    """
    Verifies all cartesian points by comparing them
    to the corresponding distance and prints the result
    """
    def verify_all_distances(self, tolerance = 1e-4):
        self.validate_cartesian_points()

        valid_points = 0   # Counts validated points
        total_points = len(self.cartesian_points)

        for i in range(total_points):
            if self.verify_distance(i, tolerance):
                valid_points += 1

        ratio  = 100.0 * valid_points / total_points

        print(f"Distance validation: {valid_points}/{total_points} points correct. "
              f"Ratio: {ratio:.2f}% within tolerance of {tolerance}")
        
        return valid_points, total_points, ratio
    
    def export_to_ply(self, output_path : str):
        self.validate_cartesian_points()

        num_points = len(self.cartesian_points)

        with open(output_path, "w") as f:
            # Write PLY header
            f.write("ply\n")
            f.write("format ascii 1.0\n")
            f.write(f"element vertex {num_points}\n")
            f.write("property float x\n")
            f.write("property float y\n")
            f.write("property float z\n")
            f.write("property ushort intensity\n")
            f.write("end_header\n")

            # Write PLY data
            for x, y, z, intensity in self.cartesian_points:
                f.write(f"{x:.6f} {y:.6f} {z:.6f} {intensity}\n")
            
        print(f"PLY file is written succesfully to {output_path}")

    def visualize_matplotlib(self):
        import matplotlib.pyplot as plt

        self.validate_cartesian_points()

        xs = [p[0] for p in self.cartesian_points]
        ys = [p[1] for p in self.cartesian_points]
        zs = [p[2] for p in self.cartesian_points]
        intensities = [p[3] for p in self.cartesian_points]

        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection="3d")

        scatter = ax.scatter(
            xs, ys, zs,
            c=intensities,
            s=1,
            cmap="viridis")

        ax.set_xlabel("X [m]")
        ax.set_ylabel("Y [m]")
        ax.set_zlabel("Z [m]")
        ax.set_title("Atrisense 360 Point Cloud")

        cbar = plt.colorbar(scatter)
        cbar.set_label("Intensity")

        plt.show()

# End of BinaryDecoder class 
#############################

ENABLE_VALIDATION = True

def run():
    input_file = "atrisense.bin"
    output_file = "atrisense_point_cloud.ply"

    try:
        if not os.path.isfile(input_file):
            raise FileNotFoundError(f"Input file not found: {input_file}")

        decoder = BinaryDecoder(input_file)
        decoder.read_binary()
        decoder.decode_records()
        decoder.convert_angles()
    
        # (Optional) Cartesian point validation
        if ENABLE_VALIDATION:
            decoder.verify_all_distances(tolerance = 1e-4)

        decoder.export_to_ply(output_file)
        decoder.visualize_matplotlib()
   
    except FileNotFoundError as e:
        print(f"[ERROR] {e}")
        sys.exit(1)

    except ValueError as e:
        print(f"[ERROR] Invalid data: {e}")
        sys.exit(2)

    except Exception as e:
        # For all the other unexpected errors
        print(f"[ERROR] Unexpected failure: {e}")
        sys.exit(3)


if __name__ == "__main__":
    run()
