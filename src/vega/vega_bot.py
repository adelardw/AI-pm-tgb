import numpy as np
from collections import defaultdict
import time
from vega.vega_config import VadConfig, GenerationConfig
from src.agents import tgc_mas, MakeRoutingMultiAgents
from beautylogger.bl import logger
from vega.vega_stream import VEGA

class VEGABot(VEGA):

    sample_rate = 16000
    num_channels = 1
    repo_name = 'openai/whisper-small'
    whisper_kwargs = GenerationConfig().model_dump()
    vad_kwargs = VadConfig(sample_rate=sample_rate).model_dump()

    def __init__(self, mas: MakeRoutingMultiAgents = tgc_mas):
        super().__init__(mas)

        self._initial_whisper()

    def _initial_vad(self):
        pass

    def stream(self):
        pass

    def audio_callback(self, indata, frames, time_info, status):
        pass

    def __call__(self, audio: np.ndarray):

        return self.transcribe(audio)

