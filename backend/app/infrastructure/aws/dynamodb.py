from __future__ import annotations

from functools import lru_cache
from typing import Any

import boto3
from botocore.config import Config as BotoConfig

from app.core.config import get_settings


@lru_cache(maxsize=1)
def get_dynamodb_resource() -> Any:
    """
    Return a cached boto3 DynamoDB resource.

    The resource is created lazily so local PostgreSQL development does not
    require AWS credentials or network access.
    """

    settings = get_settings()

    kwargs: dict[str, Any] = {
        "region_name": settings.aws_region,
        "config": BotoConfig(
            retries={
                "max_attempts": 3,
                "mode": "standard",
            }
        ),
    }

    if settings.aws_endpoint_url:
        kwargs["endpoint_url"] = settings.aws_endpoint_url

    return boto3.resource("dynamodb", **kwargs)


def get_dynamodb_table():
    """
    Return the configured AgentTrace DynamoDB table.
    """

    settings = get_settings()

    if not settings.dynamodb_table:
        raise RuntimeError("DYNAMODB_TABLE is not configured.")

    resource = get_dynamodb_resource()

    return resource.Table(settings.dynamodb_table)


def clear_dynamodb_cache() -> None:
    """
    Clear the cached boto3 resource.

    Useful for tests that change AWS configuration.
    """

    get_dynamodb_resource.cache_clear()
