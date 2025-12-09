import logging
from typing import Optional

from component.halo.base import BaseHTTPClient
from configs import config

logger = logging.getLogger(__name__)


class AduibAIClient(BaseHTTPClient):
    """带认证的 AduibAI API 客户端"""

    def __init__(self):
        """初始化 AduibAI 客户端。"""
        super().__init__(
            base_url=config.ADUIB_SERVICE_URL,
            timeout=config.ADUIB_SERVICE_TIMEOUT,
        )
        self._authenticated = False

    def authenticate(self) -> None:
        """
        与 AduibAI 服务器进行认证。

        异常:
            ConfigurationError：未配置认证方式
            AuthenticationError：认证失败
        """
        # Try token authentication first
        token = config.ADUIB_SERVICE_TOKEN
        if token:  # Type guard to ensure token is not None
            self.set_auth_token(token)
            self._authenticated = True
            logger.info("使用令牌认证成功")
            return

    def ensure_authenticated(self) -> None:
        """确保客户端已通过认证。"""
        if not self._authenticated:
            self.authenticate()


# Global aduib_ai client instance
aduib_ai_client: Optional[AduibAIClient] = None


def get_aduib_ai_client() -> AduibAIClient:
    """获取或创建 aduib_ai 客户端实例。"""
    global aduib_ai_client
    if aduib_ai_client is None:
        aduib_ai_client = AduibAIClient()
        # settings.halo_base_url = config.HALO_BASE_URL
        # settings.halo_token = config.HALO_API_KEY
        # settings.mcp_timeout = config.HALO_TIMEOUT
        aduib_ai_client.connect()
        aduib_ai_client.authenticate()
        logger.info("aduib_ai 客户端已初始化")
    return aduib_ai_client
