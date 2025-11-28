import logging
from datetime import datetime
from typing import Any, Dict
from typing import Optional

from halo_mcp_server.tools.post_tools import markdown_to_html
from slugify import slugify

from component.halo.halo_client import HaloClient, get_halo_client
from models import get_db
from models.document import KnowledgeDocument

logger = logging.getLogger(__name__)

def create_post(client: HaloClient, args: Dict[str, Any]) -> Optional[str]:
    """
    创建一篇新文章。

    参数:
        client: Halo API 客户端
        args: 工具参数

    返回:
        操作结果消息
    """
    try:
        title = args.get("title")
        content = args.get("content")

        # 若未提供则自动生成 slug
        slug = args.get("slug") or slugify(title)

        content_obj = {
            "raw": content,
            "content": content,
            "rawType": args.get("content_format")
        }

        # 构建文章数据 - 参考 Java 版本的正确结构
        # 注意：post 和 content 是两个独立的对象！
        post_data = {
            "post": {
                "apiVersion": "content.halo.run/v1alpha1",
                "kind": "Post",
                "metadata": {
                    "name": f"post-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    "annotations": {},
                },
                "spec": {
                    "title": title,
                    "slug": slug,
                    "releaseSnapshot": "",
                    "headSnapshot": "",
                    "baseSnapshot": "",
                    "owner": "",
                    "template": "",
                    "cover": args.get("cover", ""),
                    "deleted": False,
                    "publish": False,
                    "publishTime": None,
                    "pinned": args.get("pinned", False),
                    "allowComment": args.get("allow_comment", True),
                    "visible": args.get("visible", "PUBLIC"),
                    "priority": 0,
                    "excerpt": {
                        "autoGenerate": True,
                        "raw": args.get("excerpt", ""),
                    },
                    "categories": args.get("categories", []),
                    "tags": args.get("tags", []),
                    "htmlMetas": [],
                },
            },
            "content": {
                "raw": content_obj["raw"],
                "content": markdown_to_html(content),
                "rawType": content_obj["rawType"],
            },
        }

        logger.debug(f"正在创建文章：{title}")

        client.ensure_authenticated()
        result = client.post("/apis/api.console.halo.run/v1alpha1/posts", json=post_data)
        post_name = result.get("metadata", {}).get("name", "")

        # 若请求则立即发布
        if args.get("publish_immediately", False):
            client.put(
                f"/apis/api.console.halo.run/v1alpha1/posts/{post_name}/publish",
                params={"async": "true"},
            )

    except Exception as e:
        logger.error(f"创建文章出错：{e}", exc_info=True)

class BlogSyncService:
    @staticmethod
    def sync_blogs():
        # Placeholder for blog synchronization logic
        logger.info("Starting blog synchronization...")
        halo_client_ = get_halo_client()
        with get_db() as session:
            try:
                blog_list:list[KnowledgeDocument] = session.query(KnowledgeDocument).filter_by(push_status=0,doc_from='web_memo').all()
                for blog in blog_list:
                    # Simulate synchronization process
                    logger.info(f"Synchronizing blog: {blog.title}")
                    if len(blog.title)==0:
                        blog.title = blog.content[:20]  # Set a default title if empty
                    create_post(halo_client_,{
                        "title": blog.title,
                        "content": blog.content,
                        "content_format": "MARKDOWN",
                        "tags": [],
                        "categories": [],
                        "publish_immediately": True
                    })
                    # Update push_status to 1 (synchronized)
                    blog.push_status = 1
                    blog.push_time=datetime.now()
                    session.add(blog)
                session.commit()
                logger.info("Blog synchronization completed successfully.")
            except Exception as e:
                logger.error(f"Error during blog synchronization: {e}")
                session.rollback()
