"""Halo API 客户端"""
from typing import Optional

from loguru import logger

from component.halo.base import BaseHTTPClient
from configs import config


class HaloClient(BaseHTTPClient):
    """带认证的 Halo API 客户端"""

    def __init__(self):
        """初始化 Halo 客户端。"""
        super().__init__(
            base_url=config.HALO_BASE_URL,
            timeout=config.HALO_TIMEOUT,
        )
        self._authenticated = False

    def authenticate(self) -> None:
        """
        与 Halo 服务器进行认证。

        异常:
            ConfigurationError：未配置认证方式
            AuthenticationError：认证失败
        """
        # Try token authentication first
        token = config.HALO_API_KEY
        if token:  # Type guard to ensure token is not None
            self.set_auth_token(token)
            self._authenticated = True
            logger.info("使用令牌认证成功")
            return

    def ensure_authenticated(self) -> None:
        """确保客户端已通过认证。"""
        if not self._authenticated:
            self.authenticate()


# Global Halo client instance
halo_client: Optional[HaloClient] = None

def get_halo_client() -> HaloClient:
    """获取或创建 Halo 客户端实例。"""
    global halo_client
    if halo_client is None:
        halo_client = HaloClient()
        # settings.halo_base_url = config.HALO_BASE_URL
        # settings.halo_token = config.HALO_API_KEY
        # settings.mcp_timeout = config.HALO_TIMEOUT
        halo_client.connect()
        halo_client.authenticate()
        logger.info("Halo 客户端已初始化")
    return halo_client
