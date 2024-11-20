import logging
from flask import Flask
from superdesk.http_proxy import HTTPProxy, register_http_proxy


logger = logging.getLogger(__name__)


def init_app(app: Flask) -> None:
    belga_ai_url = app.config.get("BELGA_AI_URL")
    if belga_ai_url is None:
        logger.warning(
            "'BELGA_AI_URL' config not set, HTTP Proxy will not be available"
        )
        return

    register_http_proxy(
        app,
        HTTPProxy(
            endpoint_name="belga.ai_proxy",
            internal_url="belga/ai",
            external_url=belga_ai_url,
        ),
    )
