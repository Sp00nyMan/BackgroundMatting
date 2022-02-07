import json
from base64 import b64encode, b64decode
from io import BytesIO

import numpy as np
from PIL import Image


class Encoding:
    @staticmethod
    def image_from_bytes(pixels: bytes, shape, fmt='RGBA') -> Image.Image:
        array = np.frombuffer(pixels, 'uint8').reshape((shape[0], shape[1], 3 if fmt == 'RGB' else 4))
        image = Image.fromarray(array, fmt)
        if fmt == 'RGBA':
            image = image.convert('RGB')
        return image

    @staticmethod
    def json_from_bytes(pixels: bytes, shape):
        image = Encoding.image_from_bytes(pixels, shape)
        encoded = Encoding.image_to_b64(image)

        data = {
            "data": {
                "b64": encoded
            }
        }
        data = json.dumps({'instances': [data]})

        return data

    @staticmethod
    def image_from_b64(data: str) -> Image.Image:
        decoded = b64decode(data)
        data = Image.open(BytesIO(decoded))
        return data


    @staticmethod
    def image_to_b64(image: Image.Image):
        buffer = BytesIO()
        image.save(buffer, 'jpeg')
        buffer = buffer.getvalue()
        encoded = b64encode(buffer).decode()
        return encoded


