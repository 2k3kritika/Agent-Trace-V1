from __future__ import annotations

import asyncio
from typing import Any

from app.infrastructure.aws.dynamodb import get_dynamodb_table
from app.repositories.interfaces import UserRepository


class DynamoDBUserRepository(UserRepository):
    """
    DynamoDB user repository.

    Users are keyed by their generated user ID while email lookup uses
    a dedicated email entity.
    """

    def __init__(self) -> None:
        self.table = get_dynamodb_table()

    @staticmethod
    def _user_key(user_id: str) -> dict[str, str]:
        return {
            "PK": f"USER#{user_id}",
            "SK": "METADATA",
        }

    @staticmethod
    def _email_key(email: str) -> dict[str, str]:
        return {
            "PK": f"USER_EMAIL#{email.lower()}",
            "SK": "LOOKUP",
        }

    @staticmethod
    def _to_dict(item: dict[str, Any]) -> dict[str, Any]:
        return {
            "user_id": item["user_id"],
            "email": item["email"],
            "password_hash": item["password_hash"],
            "display_name": item.get("display_name"),
            "is_active": bool(item.get("is_active", True)),
            "role": item.get("role", "viewer"),
        }

    def _build_item(self, user: Any) -> dict[str, Any]:
        return {
            **self._user_key(user.user_id),
            "entity_type": "user",
            "entity_id": user.user_id,
            "user_id": user.user_id,
            "email": user.email.lower(),
            "password_hash": user.password_hash,
            "display_name": user.display_name,
            "is_active": user.is_active,
            "role": (
                user.role.value
                if hasattr(user.role, "value")
                else str(user.role)
            ),
        }

    async def get_by_id(self, user_id: str) -> Any:
        response = await asyncio.to_thread(
            self.table.get_item,
            Key=self._user_key(user_id),
        )

        item = response.get("Item")

        if item is None:
            raise KeyError(f"User '{user_id}' was not found")

        return self._to_dict(item)

    async def get_active_by_id(self, user_id: str) -> Any | None:
        response = await asyncio.to_thread(
            self.table.get_item,
            Key=self._user_key(user_id),
        )

        item = response.get("Item")

        if item is None or not item.get("is_active", False):
            return None

        return self._to_dict(item)

    async def get_by_email(self, email: str) -> Any | None:
        normalized_email = email.lower()

        lookup = await asyncio.to_thread(
            self.table.get_item,
            Key=self._email_key(normalized_email),
        )

        lookup_item = lookup.get("Item")

        if lookup_item is None:
            return None

        user_id = lookup_item.get("user_id")

        if not user_id:
            return None

        response = await asyncio.to_thread(
            self.table.get_item,
            Key=self._user_key(user_id),
        )

        item = response.get("Item")

        if item is None:
            return None

        return self._to_dict(item)

    async def email_exists(self, email: str) -> bool:
        user = await self.get_by_email(email)
        return user is not None

    async def create(self, user: Any) -> Any:
        item = self._build_item(user)

        email_item = {
            **self._email_key(user.email),
            "entity_type": "user_email_lookup",
            "entity_id": user.user_id,
            "user_id": user.user_id,
            "email": user.email.lower(),
        }

        def operation() -> None:
            self.table.put_item(Item=item)
            self.table.put_item(Item=email_item)

        await asyncio.to_thread(operation)

        return self._to_dict(item)

    async def create_unique(self, user: Any) -> Any:
        item = self._build_item(user)

        email_item = {
            **self._email_key(user.email),
            "entity_type": "user_email_lookup",
            "entity_id": user.user_id,
            "user_id": user.user_id,
            "email": user.email.lower(),
        }

        def operation() -> None:
            self.table.put_item(
                Item=item,
                ConditionExpression="attribute_not_exists(PK)",
            )
            self.table.put_item(
                Item=email_item,
                ConditionExpression="attribute_not_exists(PK)",
            )

        await asyncio.to_thread(operation)

        return self._to_dict(item)

    async def update(self, user: Any) -> Any:
        item = self._build_item(user)

        await asyncio.to_thread(
            self.table.put_item,
            Item=item,
        )

        return self._to_dict(item)