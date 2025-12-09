import logging

import pytz
from celery import Celery
from celery.schedules import crontab
import os
import urllib.parse


from configs import config

logger = logging.getLogger(__name__)

# Broker 地址可通过环境变量 CELERY_BROKER_URL 覆盖（默认使用本地 Redis）
# 支持可选的 REDIS_USERNAME / REDIS_PASSWORD / REDIS_USE_SSL（来自 config 或环境变量）
redis_username = config.REDIS_USERNAME
redis_password = config.REDIS_PASSWORD
# 对 username/password 做 URL 编码
user_enc = urllib.parse.quote_plus(redis_username) if redis_username else ""
pass_enc = urllib.parse.quote_plus(redis_password) if redis_password else ""

if user_enc and pass_enc:
    auth_part = f"{user_enc}:{pass_enc}@"
elif pass_enc:
    # 没有用户名但有密码时 Redis URL 格式为 :password@host
    auth_part = f":{pass_enc}@"
else:
    auth_part = ""

scheme = "redis"

BROKER_URL = f"{scheme}://{auth_part}{config.REDIS_HOST}:{config.REDIS_PORT}/0"
BACKEND_URL = "redis"

celery_app = Celery(config.APP_NAME, broker=BROKER_URL, backend=BACKEND_URL)

celery_app.conf.update(
        worker_log_format=config.LOG_FORMAT,
        worker_task_log_format=config.LOG_FORMAT,
        timezone=pytz.timezone(config.LOG_TZ or "UTC"),
        task_ignore_result=True,
        worker_logfile=config.LOG_FILE,
    )

# 简单的 beat schedule：每天 01:00 执行任务
celery_app.conf.beat_schedule = {
    "daily_blog_sync": {
        "task": "scheduled.scheduled_tasks.blog_sync",
        "schedule": crontab(minute="*/2"),  # 每 2 分钟执行一次
    },
    # "clean_knowledge_documents": {
    #     "task": "scheduled.scheduled_tasks.clean_knowledge_documents",
    #     "schedule": crontab(minute="*/2"),
    # },
    "blog_rag_rebuild": {
        "task": "scheduled.scheduled_tasks.blog_rag_retry",
        "schedule": crontab(hour="*/1"),  # 每小时执行一次
    },
}
celery_app.conf.update(
    imports=["scheduled.scheduled_tasks"]
)

# 方便其他模块导入
__all__ = ("celery_app",)
