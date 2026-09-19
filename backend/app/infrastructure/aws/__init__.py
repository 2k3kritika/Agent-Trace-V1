from app.infrastructure.aws.dynamodb import (
    get_dynamodb_resource,
    get_dynamodb_table,
)

__all__ = [
    "get_dynamodb_resource",
    "get_dynamodb_table",
]