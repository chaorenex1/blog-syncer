from datetime import datetime
from celery_app import celery_app
from service.blog_sync_service import BlogSyncService
import asyncio
import logging

logger = logging.getLogger(__name__)


@celery_app.task
def blog_sync():
    """打印当前时间（供 Celery 定时任务调用）。"""
    now = datetime.now()
    # 使用 ISO 格式输出本地时间
    print(f"[scheduled_tasks.print_time] current time: {now.isoformat()}")

    try:
        BlogSyncService.sync_blogs()
    except Exception as e:
        logger.exception("Error while running BlogSyncService.sync_blogs: %s", e)

    return now.isoformat()


@celery_app.task
def blog_rag_retry():
    """重试博客 RAG 处理失败的任务（供 Celery 定时任务调用）。"""
    BlogSyncService.blog_rag_retry()


@celery_app.task
def clean_knowledge_documents():
    """清理知识文档（供 Celery 定时任务调用）。"""
    BlogSyncService.clean_knowledge_documents()
