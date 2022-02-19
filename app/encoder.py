import json
from base64 import b64encode, b64decode
from io import BytesIO

import numpy as np
from PIL import Image


class Encoding:
    @staticmethod
    def _image_from_bytes(pixels: bytes, shape) -> Image.Image:
        w, h = max(shape), min(shape)
        array = np.frombuffer(pixels, 'uint8').reshape((h, w, 4))
        image = Image.fromarray(array, "RGBA")
        image = image.convert('RGB')
        return image

    @staticmethod
    def _image_from_b64(data: str) -> Image.Image:
        decoded = b64decode(data)
        data = Image.open(BytesIO(decoded))
        return data

    @staticmethod
    def _image_to_b64(image: Image.Image):
        buffer = BytesIO()
        image.save(buffer, 'jpeg')
        buffer = buffer.getvalue()
        encoded = b64encode(buffer).decode()
        return encoded

    @staticmethod
    def json_from_bytes(pixels: bytes, shape):
        image = Encoding._image_from_bytes(pixels, shape)
        encoded = Encoding._image_to_b64(image)

        data = {
            "data": {
                "b64": encoded
            }
        }
        data = json.dumps({'instances': [data]})

        return data

    @staticmethod
    def bytes_from_b64(data: str) -> bytes:
        image = Encoding._image_from_b64(data)
        bytes = image.tobytes()
        return bytes