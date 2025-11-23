import asyncio
from aiogram import Bot
from datetime import datetime, timedelta
from typing import Literal, List, Optional
import pytz
from pydantic import BaseModel, Field
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.redis import RedisJobStore
from dateutil.rrule import rrulestr
from src.beautylogger import logger
from dateutil import parser
from src.scheduler_manager import scheduler, send_telegram_notification


def schedule_event_action(
    summary: str,
    start: str,
    end: str,
    description: str,
    location: str,
    timezone: str,
    remind_format: str,
    remind_num: int,
    remind_method: str,
    recurrence: list[str],
    user_id: int = None,
    **kwargs
) -> str:
    
    if user_id is None:
        return "Ошибка: Не удалось определить пользователя."

    try:
        tz = pytz.timezone(timezone)
        
        try:
            start_dt = datetime.fromisoformat(start)
        except ValueError:
            start_dt = parser.parse(start)

        try:
            end_dt = datetime.fromisoformat(end)
        except ValueError:
            end_dt = parser.parse(end)

        if start_dt.tzinfo is None: start_dt = tz.localize(start_dt)
        if end_dt.tzinfo is None: end_dt = tz.localize(end_dt)

        event_duration = end_dt - start_dt
        
        delta_kwargs = {remind_format: remind_num}
        reminder_delta = timedelta(**delta_kwargs)

        event_occurrences = []
        rrule_raw = ""

        if not recurrence:
            event_occurrences.append(start_dt)
        else:
            rrule_raw = recurrence[0]
            rrule_clean = rrule_raw.replace("RRULE:", "")
            
            start_dt_naive = start_dt.replace(tzinfo=None)
            
            try:
                rule = rrulestr(rrule_clean, dtstart=start_dt_naive)
                count = 0
                for dt in rule:
                    dt_aware = tz.localize(dt)
                    event_occurrences.append(dt_aware)
                    count += 1
                    if count > 50: break 
            except Exception:
                event_occurrences.append(start_dt)

        jobs_count = 0
        
        for event_start_time in event_occurrences:
            remind_time = event_start_time - reminder_delta
            
            if "FREQ=MINUTELY" in rrule_raw:
                current_end_time = end_dt 

                if event_start_time >= current_end_time:
                    continue
            else:
                current_end_time = event_start_time + event_duration

            if remind_time < datetime.now(tz):
                continue

            scheduler.add_job(
                send_telegram_notification,
                trigger='date',
                run_date=remind_time,
                kwargs={
                    'user_id': user_id, 
                    'summary': summary, 
                    'description': description,
                    'start_str': event_start_time.strftime("%d.%m.%Y %H:%M"),
                    'end_str': current_end_time.strftime("%H:%M"),
                    'location': location
                },
                id=f"evt_{user_id}_{int(remind_time.timestamp())}_{jobs_count}",
                replace_existing=True,
                misfire_grace_time=3600
            )
            jobs_count += 1

        text = (
            f"🔔 [Напоминание]: {summary}\n"
            f"🕒 [Время]: {event_start_time.strftime("%d.%m.%Y %H:%M")} - {current_end_time.strftime("%H:%M")} \n"
            f"📍 [Место]: {location}\n"
            f"📝 [Описание]: {description}"
        )
        
        
        return f"✅ Событие: \n {text} \n Успешно запланировано! Напоминаний создано: {jobs_count}."

    except Exception as e:
        logger.error(f"Critical Schedule Exception: {e}", exc_info=True)
        return f"❌ Ошибка: {str(e)}"
    

NOTIFICATION_TOOL = [schedule_event_action]