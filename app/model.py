from threading import Thread, Event
import requests
from time import perf_counter, sleep
from logging_utils import get_logger
logger = get_logger(__name__)
from kivy.event import EventDispatcher

from encoder import Encoding

class Model(EventDispatcher):
    MODELS_DIR = 'models'

    def __init__(self, mode='online', *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert mode in ['online', 'local']
        self.online = mode == 'online'
        self.initialized = False

        self.register_event_type('on_initialized')
        self.register_event_type('on_init_failed')
        self.__init_process : Thread = None
        self.__init_stop = Event()


    def on_initialized(self, *args):
        pass
    def on_init_failed(self, *args):
        pass

    def interrupt_initialization(self):
        if self.__init_process is not None and  self.__init_process.is_alive():
            self.__init_stop.set()
            self.__init_process = None
            logger.info("Initialization interrupted")
            self.dispatch("on_init_failed")

    def initialize(self):
        if self.online:
            self.__init_process = Thread(target=self.__initialize_online)
            self.__init_process.start()
        else:
            self._initialize_local()

    def __initialize_online(self):
        # self.url = 'http://matting.northeurope.azurecontainer.io:8080/'
        self.url = 'http://192.168.0.160:8080/'
        self.prediction_path = 'predictions/matting'
        self.health_path = 'ping'
        self.headers = {'Content-Type':'application/json',
                        'charset':'utf-8'}

        logger.info("Checking servers availability...")
        max_tries = 3
        sleep_duration = 2
        for tries in range(max_tries):
            if self.__init_stop.is_set():
                return
            try:
                response = requests.get(url=self.url + self.health_path, timeout=1)
                response.raise_for_status()
                logger.info("Successfully initialized online inference")
                break
            except Exception as e:
                logger.debug(f"An error occurred while connecting to the server: {e}")
                logger.info(f"Retrying in {sleep_duration} seconds [{tries + 1}/{max_tries}]")
                sleep(sleep_duration)
        else:
            logger.error(f"Unable to reach {self.url}")
            self.dispatch("on_init_failed")
            return
        self.initialized = True
        self.dispatch('on_initialized')

    def _process_online(self, pixels, shape):
        start = perf_counter()
        data = Encoding.json_from_bytes(pixels, shape)
        logger.debug(f"Preprocessing: {perf_counter() - start:.4}")

        start = perf_counter()
        response = requests.post(url=self.url + self.prediction_path, data=data, headers=self.headers)
        r = response.elapsed.total_seconds()
        logger.debug(f"Request time:{r:.4}")
        logger.debug(f"Additionally elapsed {perf_counter() - start - r:.2} to receive the data")

        response.raise_for_status()
        logger.debug("Successfully received response from the server")

        start = perf_counter()

        data = response.json()
        data = data['predictions'][0]
        data = Encoding.bytes_from_b64(data)
        logger.debug(f"Postprocessing: {perf_counter() - start:.4}")

        return data

    def process(self, pixels, shape):
        image = pixels
        if self.online:
            return self._process_online(image, shape)
        else:
            return self._process_local(image)

    def _initialize_local(self):
        raise NotImplementedError()


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
