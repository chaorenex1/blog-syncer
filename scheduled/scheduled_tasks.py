from datetime import datetime
from celery_app import app


@app.task(name="scheduled.scheduled_tasks.blog_sync")
def blog_sync():
    """打印当前时间（供 Celery 定时任务调用）。"""
    now = datetime.now()
    # 使用 ISO 格式输出本地时间
    print(f"[scheduled_tasks.print_time] current time: {now.isoformat()}")

    return now.isoformat()

