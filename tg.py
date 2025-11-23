import asyncio
import logging
from src.tgbot.bot import bot, dp 
from src.scheduler_manager import scheduler
from src.beautylogger import logger

async def main():
    logger.info('🚀 Запуск приложения...')

    scheduler.start()
    jobs = scheduler.get_jobs()
    logger.info(f"📊 Задач в Redis сейчас: {len(jobs)}")
    for job in jobs:
        logger.info(f"   >>> Job ID: {job.id} | Время запуска: {job.next_run_time}")

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())