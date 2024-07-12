from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Dict, Literal, Optional, cast

from aiogram import Bot
from aiogram.fsm.state import State
from aiogram.fsm.storage.base import (
    DEFAULT_DESTINY,
    BaseEventIsolation,
    BaseStorage,
    StateType,
    StorageKey,
)
from asgiref.sync import sync_to_async
from django.core.exceptions import ObjectDoesNotExist

from app.apps.pish.models import Storage


class KeyBuilder(ABC):
    """
    Base class for Redis key builder
    """

    @abstractmethod
    def build(self, key: StorageKey, part: Literal["data", "state", "lock"]) -> str:
        """
        This method should be implemented in subclasses

        :param key: contextual key
        :param part: part of the record
        :return: key to be used in Redis queries
        """
        pass


class DefaultKeyBuilder(KeyBuilder):
    """
    Simple Redis key builder with default prefix.

    Generates a colon-joined string with prefix, chat_id, user_id,
    optional bot_id and optional destiny.
    """

    def __init__(
        self,
        *,
        prefix: str = "fsm",
        separator: str = ":",
        with_bot_id: bool = False,
        with_destiny: bool = False,
    ) -> None:
        """
        :param prefix: prefix for all records
        :param separator: separator
        :param with_bot_id: include Bot id in the key
        :param with_destiny: include destiny key
        """
        self.prefix = prefix
        self.separator = separator
        self.with_bot_id = with_bot_id
        self.with_destiny = with_destiny

    def build(self, key: StorageKey, part: Literal["data", "state", "lock"]) -> str:
        parts = [self.prefix]
        if self.with_bot_id:
            parts.append(str(key.bot_id))
        parts.extend([str(key.chat_id), str(key.user_id)])
        if self.with_destiny:
            parts.append(key.destiny)
        elif key.destiny != DEFAULT_DESTINY:
            raise ValueError(
                "Redis key builder is not configured to use key destiny other the default.\n"
                "\n"
                "Probably, you should set `with_destiny=True` in for DefaultKeyBuilder.\n"
                "E.g: `RedisStorage(redis, key_builder=DefaultKeyBuilder(with_destiny=True))`"
            )
        parts.append(part)
        return self.separator.join(parts)


class DjangoStorage(BaseStorage):
    def __init__(
        self,
        key_builder: Optional[KeyBuilder] = None
    ) -> None:
        """
        :param key_builder: builder that helps to convert contextual key to string
        """
        if key_builder is None:
            key_builder = DefaultKeyBuilder()
        self.key_builder = key_builder

    async def set_state(
        self,
        bot: Bot,
        key: StorageKey,
        state: StateType = None,
    ) -> None:
        django_key = self.key_builder.build(key, "state")
        if state is None:
            await Storage.objects.filter(key=django_key).adelete()
        else:
            try:
                old_state = await Storage.objects.aget(key=django_key)
                setattr(old_state, "state", cast(str, state.state if isinstance(state, State) else state))
                await sync_to_async(old_state.save)(update_fields=["state"])
            except Storage.DoesNotExist:
                await Storage.objects.acreate(
                    key=django_key,
                    state=cast(str, state.state if isinstance(state, State) else state)
                )

    async def get_state(
        self,
        bot: Bot,
        key: StorageKey,
    ) -> Optional[str]:
        django_key = self.key_builder.build(key, "state")
        try:
            value = (await Storage.objects.values("state").aget(key=django_key))["state"]
        except ObjectDoesNotExist:
            value = None
        return cast(Optional[str], value)

    async def set_data(
        self,
        bot: Bot,
        key: StorageKey,
        data: Dict[str, Any],
    ) -> None:
        django_key = self.key_builder.build(key, "data")
        if not data:
            await Storage.objects.filter(key=django_key).adelete()
            return
        try:
            old_data = await Storage.objects.aget(key=django_key)
            setattr(old_data, "data", bot.session.json_dumps(data))
            await sync_to_async(old_data.save)(update_fields=["data"])
        except Storage.DoesNotExist:
            await Storage.objects.acreate(
                key=django_key,
                data=bot.session.json_dumps(data)
            )

    async def get_data(
        self,
        bot: Bot,
        key: StorageKey,
    ) -> Dict[str, Any]:
        django_key = self.key_builder.build(key, "data")
        try:
            value = (await Storage.objects.values("data").aget(key=django_key))["data"]
        except ObjectDoesNotExist:
            return {}
        return cast(Dict[str, Any], bot.session.json_loads(value))

    async def close(self) -> None:
        pass
