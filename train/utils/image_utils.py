from typing import Union, Optional
#from turbojpeg import TurboJPEG, TJPF
import numpy as np
import cv2
import imagesize


Array = np.ndarray
#turbo_jpeg = TurboJPEG()


def _equal_to_byte_string(buffer: Union[bytes, Array], byte_string: bytes) -> bool:
    return (buffer == byte_string) if isinstance(buffer, bytes) else all(buffer == np.frombuffer(byte_string, np.uint8))


def has_jpeg_bytes(buffer: Union[bytes, Array]) -> bool:
    """Check whether bytes array or numpy buffer comprises JPEG image or not"""
    header = buffer[6:10]
    return _equal_to_byte_string(header, b"JFIF") or _equal_to_byte_string(header, b"Exif")


# def decode_rgb_jpeg(buffer: Union[bytes, Array]) -> Array:
#     """Decode JPEG image from bytes array or numpy array"""
#     return turbo_jpeg.decode(buffer, pixel_format=TJPF.RGB)


def read_image(image_path: str) -> Array:
    with open(image_path, "rb") as fb:
        buffer = np.frombuffer(fb.read(), dtype=np.uint8)
    #use_turbo_jpeg = has_jpeg_bytes(buffer)
    use_turbo_jpeg=False
    #image = decode_rgb_jpeg(buffer) if use_turbo_jpeg else cv2.imdecode(buffer, cv2.IMREAD_UNCHANGED)
    image = cv2.imdecode(buffer, cv2.IMREAD_UNCHANGED)

    # If cv2 is used for rgb image decoding then we must convert bgr into rgb format
    try:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB) if (not use_turbo_jpeg) and (image.ndim == 3) else image
        return image
    except:
        print(image_path)


def resize_image_if_needed(image: Array, target_height: Optional[int], target_width: Optional[int], interpolation: int) -> Array:

    height, width = image.shape[:2]
    target_width = width if target_width is None else target_width
    target_height = height if target_height is None else target_height
    if (width, height) != (target_width, target_height):
        image = cv2.resize(image, dsize=(target_width, target_height), interpolation=interpolation)
    return image