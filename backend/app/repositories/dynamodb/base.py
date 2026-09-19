from __future__ import annotations

from collections.abc import Iterable
from typing import Any, Generic, TypeVar

from app.infrastructure.aws.dynamodb import get_dynamodb_table


T = TypeVar("T")


class DynamoDBRepository(Generic[T]):
    """
    Base repository for AgentTrace DynamoDB persistence.

    The repository intentionally keeps DynamoDB-specific operations here so
    higher-level services remain storage-provider agnostic.
    """

    entity_type: str = "entity"

    def __init__(self, table: Any | None = None) -> None:
        self.table = table or get_dynamodb_table()

    def _entity_key(
        self,
        entity_id: str,
    ) -> dict[str, str]:
        return {
            "PK": f"{self.entity_type.upper()}#{entity_id}",
            "SK": "METADATA",
        }

    def get_by_id_sync(
        self,
        entity_id: str,
    ) -> dict[str, Any] | None:
        response = self.table.get_item(
            Key=self._entity_key(entity_id),
            ConsistentRead=True,
        )

        item = response.get("Item")
        if item is None:
            return None

        return item

    def put_item_sync(
        self,
        item: dict[str, Any],
    ) -> dict[str, Any]:
        self.table.put_item(Item=item)
        return item

    def put_item_if_absent_sync(
        self,
        item: dict[str, Any],
    ) -> bool:
        self.table.put_item(
            Item=item,
            ConditionExpression="attribute_not_exists(PK)",
        )
        return True

    def delete_by_id_sync(
        self,
        entity_id: str,
    ) -> bool:
        response = self.table.delete_item(
            Key=self._entity_key(entity_id),
            ReturnValues="ALL_OLD",
        )

        return bool(response.get("Attributes"))

    def query_partition_sync(
        self,
        partition_key: str,
        *,
        begins_with: str | None = None,
        scan_forward: bool = True,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        expression_attribute_values = {
            ":pk": partition_key,
        }

        kwargs: dict[str, Any] = {
            "KeyConditionExpression": "PK = :pk",
            "ExpressionAttributeValues": expression_attribute_values,
            "ScanIndexForward": scan_forward,
        }

        if begins_with:
            kwargs["KeyConditionExpression"] = (
                "PK = :pk AND begins_with(SK, :sk)"
            )
            kwargs["ExpressionAttributeValues"][":sk"] = begins_with

        if limit is not None:
            kwargs["Limit"] = limit

        response = self.table.query(**kwargs)

        return list(response.get("Items", []))

    def batch_put_sync(
        self,
        items: Iterable[dict[str, Any]],
    ) -> int:
        item_list = list(items)

        if not item_list:
            return 0

        with self.table.batch_writer() as batch:
            for item in item_list:
                batch.put_item(Item=item)

        return len(item_list)