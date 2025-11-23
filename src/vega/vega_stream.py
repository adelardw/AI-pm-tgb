import soundfile as sf
from torchaudio.transforms import Vad
import numpy as np
from collections import defaultdict
from transformers import WhisperForConditionalGeneration, WhisperProcessor, pipeline
import torch
import time
from vega.vega_config import VadConfig, GenerationConfig
from src.agents import tgc_mas, MakeRoutingMultiAgents
from beautylogger.bl import logger


class VEGABase:
    def __init__(self, mas: MakeRoutingMultiAgents):
        self.mas = mas

    def stream(self, *args, **kwargs):
        pass

    def transcribe(self, *args, **kwargs):
        pass


class VEGA(VEGABase):
    """
    A class for real-time Automatic Speech Recognition (ASR) using Whisper
    and Voice Activity Detection (VAD). It continuously listens to audio,
    transcribes speech when detected, and pauses transcription during silence.
    """
    sample_rate = 16000
    block_size = 8096
    num_channels = 1
    memory_time = 20
    down_time = 3
    repo_name = 'openai/whisper-small'

    memory_buffer_size = memory_time * sample_rate

    whisper_kwargs = GenerationConfig().model_dump()
    vad_kwargs = VadConfig(sample_rate=sample_rate).model_dump()

    def __init__(self, mas: MakeRoutingMultiAgents = tgc_mas):
        super().__init__(mas)

        self.full_transcribe = defaultdict(list)
        self._initial_whisper()

    def transcribe(self, audio_array: np.ndarray) -> str:
        """
        Transcribes an audio numpy array using the pre-loaded Whisper pipeline.

        Args:
            audio_array: A numpy array containing the audio data.
                         Expected to be 1D for mono audio.

        Returns:
            The transcribed text as a string.
        """

        if audio_array.ndim > 1:
            # Если массив многомерный (например, из-за channels=1), преобразуем его в 1D
            audio_array = audio_array.flatten()

        transcription_result = self.pipe(audio_array, generate_kwargs=self.whisper_kwargs)

        transcribed_text = transcription_result['text']
        return transcribed_text


    def _initial_whisper(self):
        """
        Initializes the Whisper model and processor for Automatic Speech Recognition (ASR).
        It loads the model from Hugging Face and attempts to compile it using torch.compile
        for potential performance improvements if available.
        This method is marked as protected, indicating it's for internal use.
        """
        logger.info(f"Загрузка модели Whisper: {self.repo_name}...")
        model = WhisperForConditionalGeneration.from_pretrained(
            self.repo_name,
            cache_dir='hf_models',
            low_cpu_mem_usage=True
        )

        model = torch.compile(
            model,
            mode="max-autotune",
            fullgraph=True,
            dynamic=False)

        processor = WhisperProcessor.from_pretrained(
            self.repo_name,
            cache_dir='hf_models',
            language='ru')

        self.pipe = pipeline(
            'automatic-speech-recognition',
            model=model,
            feature_extractor=processor.feature_extractor,
            tokenizer=processor.tokenizer,
            generate_kwargs=self.whisper_kwargs
        )
        logger.info("Пайплайн Whisper инициализирован.")
    
    def __call__(self, audio: np.ndarray):

        return self.transcribe(audio)
