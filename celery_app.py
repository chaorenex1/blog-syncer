from celery import Celery
from celery.schedules import crontab
import os
import urllib.parse
from configs import config

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

BROKER_URL = os.getenv("CELERY_BROKER_URL", f"{scheme}://{auth_part}{config.REDIS_HOST}:{config.REDIS_PORT}/0")

app = Celery("blog_syncer", broker=BROKER_URL)

# 时区设置（按照本地需求调整）
app.conf.timezone = "Asia/Shanghai"
# 是否启用 UTC（如果启用则 crontab 按 UTC 调度）
app.conf.enable_utc = False

# 简单的 beat schedule：每天 01:00 执行任务
app.conf.beat_schedule = {
    "daily_print_time": {
        "task": "scheduled.scheduled_tasks.blog_sync",
        "schedule": crontab(hour=1, minute=0),
        "options": {"queue": "default"},
    },
}

# 方便其他模块导入
__all__ = ("app",)
