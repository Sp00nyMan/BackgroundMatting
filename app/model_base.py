import numpy as np
import requests
from time import perf_counter

# from kivy.utils import platform
# from jnius import autoclass
#
# if platform == 'android':
#     Interpreter = autoclass('org.pytorch.LiteModuleLoader')
#     Module = autoclass('org.pytorch.Module')
#     Tensor = autoclass('org.pytorch.Tensor')
#     IValue = autoclass('org.pytorch.IValue')
#     ToTensor = None
from PIL import Image

from encoder import Encoding

class Model:
    MODELS_DIR = 'models'

    def __init__(self, mode='online', num_threads=None):
        assert mode in ['online', 'local']
        self.num_threads = num_threads
        self.online = mode == 'online'
        if self.online:
            self.__initialize_online()
        else:
            self._initialize_local()

    #TODO: Find a service that provides fast enough GPU Inference
    def __initialize_online(self):
        #self.url = 'http://matting.northeurope.azurecontainer.io:8080/predictions/matting'
        self.url = 'http://192.168.0.160:8080/predictions/matting'
        self.headers = {'Content-Type':'application/json',
                        'charset':'utf-8'}

    def _process_online(self, pixels, shape):
        data = Encoding.json_from_bytes(pixels, shape)

        start = perf_counter()
        response = requests.post(url=self.url, data=data, headers=self.headers)
        print(f"Request: {perf_counter() - start:.4}")
        print(f"Elapsed: {response.elapsed}")

        response.raise_for_status()

        data = response.json()
        data = data['predictions'][0]
        data = Encoding.image_from_b64(data).tobytes()

        return data

    def process(self, pixels, shape):
        image = pixels
        if self.online:
            return self._process_online(image, shape)
        else:
            return self._process_local(image)

#TODO: Local inference
"""
    def _initialize_local(self):
        self.model = None
        self.rec = np.array([0.] * 4).astype('float32')
        self.downsample_ratio = np.float32(1.)
        self.model: Module = Interpreter.load(os.path.join(os.getcwd(), self.MODELS_DIR, 'resnet50.ptl'))

    def _preprocess(self, input_image: np.ndarray):
        if input_image.shape[-1] == 4:
            input_image = cv2.cvtColor(input_image, cv2.COLOR_RGBA2RGB)
        input_image = np.expand_dims(input_image, 0)
        input_image = input_image.astype('float32')
        input_image = np.divide(input_image, 255)
        return input_image

    def _process_local(self, input_image):
        image = self._preprocess(input_image)

        self.model.forward(IValue.from(image)).toTensor()

        fgr, pha = self._get_output()
        return self._postprocess(fgr, pha)
        

    def _get_output(self):
        output = []
        output_details = self.model.get_output_details()
        for t in output_details:
            output.append(self.model.get_tensor(t['index']))
        fgr, pha = output[:2]
        self.rec = output[2:]
        return fgr, pha

    def _postprocess(self, fgr, pha):
        result = np.multiply(fgr, pha)
        result = np.squeeze(result, 0)
        result = np.multiply(result, 255)
        return result
"""