import typing as tp
from pydantic import BaseModel, Field

class GenerationConfig(BaseModel):
    max_new_tokens: int = Field( 300, help="select num new tokens for generation")
    language: str =  Field("ru", help='Language')
    task: str = Field("transcribe", help='task')
    temperature: float =  Field(0.7, help="select temperature")
    do_sample: bool = Field(False, help="select sample option")
    num_beams: tp.Optional[int]  = Field(None, help="select num beams for beam search method")
    return_timestamps: bool = Field(True, help="return audio timesteps")
    early_stopping: bool = Field(False)


class VadConfig(BaseModel):
    sample_rate: int
    trigger_level: float = 5
    trigger_time: float = 0.05
    search_time: float = 1
    allowed_gap: float = 0.05
    pre_trigger_time: float = 0
    boot_time: float = 0.15
    noise_up_time: float = 0.1
    noise_down_time: float = 0.01
    noise_reduction_amount: float = 1.35
    measure_freq: float = 20
    measure_duration: float | None = None
    measure_smooth_time: float = 0.4
    hp_filter_freq: float = 50
    lp_filter_freq: float = 3000
    hp_lifter_freq: float = 150
    lp_lifter_freq: float = 2000