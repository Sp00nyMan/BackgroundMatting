import logging
logger = logging.getLogger(__file__)
logger.setLevel(logging.DEBUG)
from base64 import b64encode
from io import BytesIO
from time import perf_counter

import torch
from PIL import Image
from torchvision.transforms import Compose, ToTensor, ToPILImage
from ts.torch_handler.vision_handler import VisionHandler


class Handler(VisionHandler):
    image_processing = Compose([ToTensor()])

    def __init__(self):
        super().__init__()
        self.rec = [None] * 4
        self.bgr = None

    @staticmethod
    def image_to_b64(image: Image.Image):
        buffer = BytesIO()
        image.save(buffer, 'jpeg')
        buffer = buffer.getvalue()
        encoded = b64encode(buffer).decode()
        return encoded

    def initialize(self, context):
        super().initialize(context)
        self.model = torch.jit.script(self.model)
        self.model = torch.jit.freeze(self.model).eval()
        self.bgr = torch.tensor([120, 255, 155],dtype=torch.float32 , device=self.device).div(255).view(1, 3, 1, 1)
        self.initialized = True
        logger.info(context.system_properties)

    def preprocess(self, data):
        data : bytes = data[0]['data']
        logger.info(f"Received data of size {len(data)} B")
        image : Image.Image= Image.open(BytesIO(data))
        image = self.image_processing(image)
        image = image.unsqueeze(0).to(self.device)
        logger.info(f"Converted to an image of shape: {image.shape}")
        return image

    def postprocess(self, data):
        fgr, pha = data
        image = fgr * pha + self.bgr * (1 - pha)

        image: Image.Image = ToPILImage()(image[0])

        encoded = Handler.image_to_b64(image)
        logger.info(f"Sending data of size {len(encoded)} B")

        return [encoded]

    def inference(self, data, *args, **kwargs):
        h, w = data.shape[-2:]
        downsample_ratio = min(512 / max(h, w), 1)
        with torch.no_grad():
            fgr, pha, *self.rec = self.model(data, *self.rec, downsample_ratio)
        return fgr, pha

    def handle(self, data, context):
        start = perf_counter()
        image = self.preprocess(data)
        logger.info(f"Preprocessing time: {perf_counter() - start:.4}")

        start = perf_counter()
        output = self.inference(image)
        logger.info(f"Inference time: {perf_counter() - start:.4}")

        start = perf_counter()
        result = self.postprocess(output)
        logger.info(f"Postprocessing time: {perf_counter() - start:.4}")
        return result