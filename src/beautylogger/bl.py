from loguru import logger
import colorama
import sys


colorama.init()
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:HH:mm:ss}</green> | <level>{level.icon} {level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="DEBUG",
    colorize=True,
    enqueue=True,
    backtrace=True,
    diagnose=True,
)

logger.level("INFO", color="<bold><green>")
logger.level("CRITICAL", color="<bold><red>")
logger.level("DEBUG", color="<bold><yellow>")

logger.level("CRITICAL", icon="⛔")
logger.level("DEBUG", icon="⚠️")



'''class ElasticLogScheme(BaseModel):
    activated_agent: str = Field(..., help = 'Активируемые агент')
    activated_agent_result: str = Field(..., help = 'Ответ агента')
    transcribe: str = Field(..., help = 'Результат транскрибации')'''