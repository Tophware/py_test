#!/usr/bin/env python3
"""
Comprehensive Image Data Extractor

This script extracts all available data from image files including:
- EXIF data (camera settings, GPS, timestamps, etc.)
- Image properties (dimensions, format, color mode, etc.)
- Color analysis (histograms, dominant colors, etc.)
- File metadata (size, dates, etc.)
- Technical details (compression, bit depth, etc.)
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path
import hashlib
import mimetypes

# Third-party imports (will handle ImportError gracefully)
try:
    from PIL import Image
    from PIL.ExifTags import TAGS, GPSTAGS

    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    TAGS = {}
    GPSTAGS = {}
    print("Warning: PIL/Pillow not available. Install with: pip install Pillow")

try:
    import numpy as np

    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    print("Warning: NumPy not available. Install with: pip install numpy")

try:
    import cv2

    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    print("Warning: OpenCV not available. Install with: pip install opencv-python")


class ImageDataExtractor:
    """Extract comprehensive data from image files."""

    def __init__(self):
        self.supported_formats = {
            ".jpg",
            ".jpeg",
            ".png",
            ".tiff",
            ".tif",
            ".webp",
            ".bmp",
            ".gif",
            ".ico",
            ".pcx",
            ".ppm",
            ".pbm",
            ".pgm",
            ".pnm",
            ".sgi",
            ".tga",
            ".xbm",
        }

    def extract_all_data(self, image_path):
        """Extract all available data from an image file."""
        image_path = Path(image_path)

        if not image_path.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")

        if not image_path.suffix.lower() in self.supported_formats:
            raise ValueError(f"Unsupported image format: {image_path.suffix}")

        data = {
            "file_info": self._extract_file_info(image_path),
            "image_properties": {},
            "exif_data": {},
            "color_analysis": {},
            "technical_details": {},
            "extraction_timestamp": datetime.now().isoformat(),
        }

        if PIL_AVAILABLE:
            try:
                with Image.open(image_path) as img:
                    data["image_properties"] = self._extract_image_properties(img)
                    data["exif_data"] = self._extract_exif_data(img)
                    data["technical_details"] = self._extract_technical_details(img)

                    if NUMPY_AVAILABLE:
                        data["color_analysis"] = self._extract_color_analysis(img)
            except Exception as e:
                data["pil_error"] = str(e)

        if OPENCV_AVAILABLE:
            try:
                data["opencv_analysis"] = self._extract_opencv_data(image_path)
            except Exception as e:
                data["opencv_error"] = str(e)

        return data

    def _extract_file_info(self, image_path):
        """Extract basic file system information."""
        stat = image_path.stat()

        # Calculate file hash
        hash_md5 = hashlib.md5()
        hash_sha256 = hashlib.sha256()

        with open(image_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
                hash_sha256.update(chunk)

        return {
            "filename": image_path.name,
            "full_path": str(image_path.absolute()),
            "file_size_bytes": stat.st_size,
            "file_size_human": self._human_readable_size(stat.st_size),
            "created_time": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "accessed_time": datetime.fromtimestamp(stat.st_atime).isoformat(),
            "mime_type": mimetypes.guess_type(str(image_path))[0],
            "file_extension": image_path.suffix.lower(),
            "md5_hash": hash_md5.hexdigest(),
            "sha256_hash": hash_sha256.hexdigest(),
        }

    def _extract_image_properties(self, img):
        """Extract basic image properties using PIL."""
        return {
            "width": img.width,
            "height": img.height,
            "dimensions": f"{img.width}x{img.height}",
            "format": img.format,
            "mode": img.mode,
            "has_transparency": img.mode in ("RGBA", "LA")
            or "transparency" in img.info,
            "is_animated": getattr(img, "is_animated", False),
            "n_frames": getattr(img, "n_frames", 1),
            "aspect_ratio": round(img.width / img.height, 4),
            "megapixels": round((img.width * img.height) / 1_000_000, 2),
        }

    def _extract_exif_data(self, img):
        """Extract EXIF data from image."""
        exif_data = {}

        if hasattr(img, "_getexif") and img._getexif() is not None:
            exif = img._getexif()

            for tag_id, value in exif.items():
                tag = TAGS.get(tag_id, tag_id)

                # Handle GPS data specially
                if tag == "GPSInfo":
                    gps_data = {}
                    for gps_tag_id, gps_value in value.items():
                        gps_tag = GPSTAGS.get(gps_tag_id, gps_tag_id)
                        gps_data[gps_tag] = str(gps_value)
                    exif_data["GPS"] = gps_data

                    # Calculate decimal GPS coordinates if available
                    try:
                        coords = self._convert_gps_to_decimal(gps_data)
                        if coords:
                            exif_data["GPS_decimal"] = coords
                    except:
                        pass
                else:
                    # Convert value to string for JSON serialization
                    try:
                        # Handle special EXIF data types
                        if hasattr(value, "numerator") and hasattr(
                            value, "denominator"
                        ):
                            # IFDRational type
                            exif_data[tag] = (
                                float(value) if value.denominator != 0 else 0
                            )
                        elif isinstance(value, bytes):
                            # Convert bytes to hex string
                            exif_data[tag] = value.hex()
                        elif isinstance(value, (tuple, list)):
                            # Convert tuples/lists to string representation
                            exif_data[tag] = str(value)
                        else:
                            exif_data[tag] = (
                                str(value)
                                if not isinstance(value, (str, int, float, bool))
                                else value
                            )
                    except Exception:
                        exif_data[tag] = str(value)

        # Try to get EXIF from img.info as well
        if "exif" in img.info:
            try:
                exif_dict = img.getexif()
                for tag_id in exif_dict:
                    tag = TAGS.get(tag_id, tag_id)
                    if tag not in exif_data:  # Don't override existing data
                        exif_data[tag] = str(exif_dict[tag_id])
            except Exception:
                pass

        return exif_data

    def _extract_technical_details(self, img):
        """Extract technical image details."""
        details = {
            "color_profile": None,
            "dpi": img.info.get("dpi", None),
            "compression": img.info.get("compression", None),
            "quality": img.info.get("quality", None),
            "bits_per_pixel": None,
            "color_space": img.mode,
            "has_icc_profile": "icc_profile" in img.info,
            "transparency_info": img.info.get("transparency", None),
        }

        # Calculate bits per pixel
        mode_to_bpp = {
            "1": 1,
            "L": 8,
            "P": 8,
            "RGB": 24,
            "RGBA": 32,
            "CMYK": 32,
            "YCbCr": 24,
            "LAB": 24,
            "HSV": 24,
        }
        details["bits_per_pixel"] = mode_to_bpp.get(img.mode, None)

        # Extract ICC profile info if available
        if "icc_profile" in img.info:
            details["icc_profile_size"] = len(img.info["icc_profile"])

        # Add any other info keys
        other_info = {}
        for key, value in img.info.items():
            if key not in [
                "dpi",
                "compression",
                "quality",
                "transparency",
                "icc_profile",
            ]:
                other_info[key] = (
                    str(value)
                    if not isinstance(value, (str, int, float, bool, type(None)))
                    else value
                )

        if other_info:
            details["additional_info"] = other_info

        return details

    def _extract_color_analysis(self, img):
        """Extract color analysis using PIL and NumPy."""
        if not NUMPY_AVAILABLE:
            return {"error": "NumPy not available for color analysis"}

        analysis = {}

        try:
            # Convert to RGB if necessary
            if img.mode != "RGB":
                img_rgb = img.convert("RGB")
            else:
                img_rgb = img

            # Convert to numpy array
            img_array = np.array(img_rgb)

            # Basic statistics
            analysis["mean_color"] = {
                "red": float(np.mean(img_array[:, :, 0])),
                "green": float(np.mean(img_array[:, :, 1])),
                "blue": float(np.mean(img_array[:, :, 2])),
            }

            analysis["std_color"] = {
                "red": float(np.std(img_array[:, :, 0])),
                "green": float(np.std(img_array[:, :, 1])),
                "blue": float(np.std(img_array[:, :, 2])),
            }

            # Histograms
            analysis["histograms"] = {}
            for i, color in enumerate(["red", "green", "blue"]):
                hist, bins = np.histogram(img_array[:, :, i], bins=256, range=(0, 256))
                analysis["histograms"][color] = {
                    "values": hist.tolist(),
                    "peak_value": int(bins[np.argmax(hist)]),
                    "total_pixels": int(np.sum(hist)),
                }

            # Dominant colors (simplified - top 5 most common colors)
            pixels = img_array.reshape(-1, 3)
            unique_colors, counts = np.unique(pixels, axis=0, return_counts=True)

            # Sort by frequency
            sorted_indices = np.argsort(counts)[::-1]
            top_colors = []

            for i in range(min(5, len(unique_colors))):
                idx = sorted_indices[i]
                color = unique_colors[idx]
                count = counts[idx]
                percentage = (count / len(pixels)) * 100

                top_colors.append(
                    {
                        "color_rgb": color.tolist(),
                        "color_hex": f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}",
                        "pixel_count": int(count),
                        "percentage": round(percentage, 2),
                    }
                )

            analysis["dominant_colors"] = top_colors

            # Brightness and contrast metrics
            gray = np.dot(img_array[..., :3], [0.2989, 0.5870, 0.1140])
            analysis["brightness"] = {
                "mean": float(np.mean(gray)),
                "median": float(np.median(gray)),
                "std": float(np.std(gray)),
            }

            analysis["contrast"] = {
                "rms_contrast": float(np.std(gray)),
                "michelson_contrast": (
                    float((np.max(gray) - np.min(gray)) / (np.max(gray) + np.min(gray)))
                    if (np.max(gray) + np.min(gray)) > 0
                    else 0
                ),
            }

        except Exception as e:
            analysis["error"] = str(e)

        return analysis

    def _extract_opencv_data(self, image_path):
        """Extract additional data using OpenCV."""
        if not OPENCV_AVAILABLE:
            return {"error": "OpenCV not available"}

        try:
            img = cv2.imread(str(image_path))
            if img is None:
                return {"error": "Could not load image with OpenCV"}

            analysis = {
                "opencv_shape": img.shape,
                "opencv_dtype": str(img.dtype),
                "opencv_channels": (
                    len(img.shape) if len(img.shape) == 2 else img.shape[2]
                ),
            }

            # Calculate some basic metrics
            if len(img.shape) == 3:
                analysis["channel_means"] = {
                    "blue": float(np.mean(img[:, :, 0])),
                    "green": float(np.mean(img[:, :, 1])),
                    "red": float(np.mean(img[:, :, 2])),
                }

            # Detect edges for complexity estimation
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
            analysis["edge_density"] = float(edge_density)

            return analysis

        except Exception as e:
            return {"error": str(e)}

    def _convert_gps_to_decimal(self, gps_data):
        """Convert GPS coordinates from EXIF format to decimal degrees."""

        def dms_to_decimal(dms_str, ref):
            """Convert degrees, minutes, seconds to decimal degrees."""
            try:
                # Parse the coordinate string
                if isinstance(dms_str, str):
                    parts = dms_str.strip("()").split(", ")
                    degrees = float(parts[0])
                    minutes = float(parts[1])
                    seconds = float(parts[2])
                else:
                    degrees, minutes, seconds = dms_str

                decimal = degrees + minutes / 60 + seconds / 3600

                if ref in ["S", "W"]:
                    decimal = -decimal

                return decimal
            except:
                return None

        lat = None
        lon = None

        if "GPSLatitude" in gps_data and "GPSLatitudeRef" in gps_data:
            lat = dms_to_decimal(gps_data["GPSLatitude"], gps_data["GPSLatitudeRef"])

        if "GPSLongitude" in gps_data and "GPSLongitudeRef" in gps_data:
            lon = dms_to_decimal(gps_data["GPSLongitude"], gps_data["GPSLongitudeRef"])

        if lat is not None and lon is not None:
            return {"latitude": lat, "longitude": lon}

        return None

    def _human_readable_size(self, size_bytes):
        """Convert bytes to human readable format."""
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"

    def save_data_to_file(self, data, output_path):
        """Save extracted data to JSON file."""
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def print_summary(self, data):
        """Print a summary of the extracted data."""
        print(f"\n{'='*60}")
        print(f"IMAGE DATA EXTRACTION SUMMARY")
        print(f"{'='*60}")

        # File info
        file_info = data.get("file_info", {})
        print(f"\nFILE INFORMATION:")
        print(f"  Filename: {file_info.get('filename', 'N/A')}")
        print(f"  Size: {file_info.get('file_size_human', 'N/A')}")
        print(f"  Format: {file_info.get('mime_type', 'N/A')}")
        print(f"  Modified: {file_info.get('modified_time', 'N/A')}")

        # Image properties
        props = data.get("image_properties", {})
        if props:
            print(f"\nIMAGE PROPERTIES:")
            print(f"  Dimensions: {props.get('dimensions', 'N/A')}")
            print(f"  Format: {props.get('format', 'N/A')}")
            print(f"  Color Mode: {props.get('mode', 'N/A')}")
            print(f"  Megapixels: {props.get('megapixels', 'N/A')}")
            print(f"  Aspect Ratio: {props.get('aspect_ratio', 'N/A')}")
            if props.get("is_animated"):
                print(f"  Frames: {props.get('n_frames', 'N/A')}")

        # EXIF summary
        exif = data.get("exif_data", {})
        if exif:
            print(f"\nEXIF DATA SUMMARY:")
            important_tags = ["DateTime", "Make", "Model", "Software", "GPS_decimal"]
            for tag in important_tags:
                if tag in exif:
                    print(f"  {tag}: {exif[tag]}")

            print(f"  Total EXIF tags: {len(exif)}")

        # Color analysis summary
        color = data.get("color_analysis", {})
        if color and "dominant_colors" in color:
            print(f"\nCOLOR ANALYSIS:")
            print(
                f"  Dominant Color: {color['dominant_colors'][0]['color_hex']} ({color['dominant_colors'][0]['percentage']}%)"
            )
            if "brightness" in color:
                print(f"  Average Brightness: {color['brightness']['mean']:.1f}")

        print(f"\n{'='*60}")


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(
        description="Extract comprehensive data from image files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python image_data_extractor.py image.jpg
  python image_data_extractor.py image.jpg --output data.json
  python image_data_extractor.py image.jpg --quiet
        """,
    )

    parser.add_argument("image_path", help="Path to the image file")
    parser.add_argument("--output", "-o", help="Output JSON file path")
    parser.add_argument(
        "--quiet", "-q", action="store_true", help="Suppress summary output"
    )

    args = parser.parse_args()

    # Check if required libraries are available
    missing_libs = []
    if not PIL_AVAILABLE:
        missing_libs.append("Pillow")
    if not NUMPY_AVAILABLE:
        missing_libs.append("numpy")
    if not OPENCV_AVAILABLE:
        missing_libs.append("opencv-python")

    if missing_libs:
        print(f"Warning: Missing optional libraries: {', '.join(missing_libs)}")
        print("Install with: pip install " + " ".join(missing_libs))
        print("Some features may not be available.\n")

    try:
        # Extract data
        extractor = ImageDataExtractor()
        print(f"Extracting data from: {args.image_path}")

        data = extractor.extract_all_data(args.image_path)

        # Save to file if requested
        if args.output:
            extractor.save_data_to_file(data, args.output)
            print(f"Data saved to: {args.output}")

        # Print summary unless quiet mode
        if not args.quiet:
            extractor.print_summary(data)
        else:
            print("Extraction completed successfully.")

        # If no output file specified, print JSON to stdout
        if not args.output and not args.quiet:
            print(f"\nFull JSON data:")
            print(json.dumps(data, indent=2))

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
