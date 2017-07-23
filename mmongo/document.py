# coding: utf8

import asyncio
import logging

from mtypes import Document as _Document

from .utils import to_snake_case
from .fields import Field
from .hooks import (validate_columns_before_save,
                    log_modified_after_save)
from .errors import DocumentNotFound


class DocumentMetaClass(type):

    def __new__(cls, name, bases, attrs):
        if name == 'Document':
            return type.__new__(cls, name, bases, attrs)

        fields = []
        mapping = {}
        indexes = set()

        for n, attr in attrs.items():
            if isinstance(attr, Field):
                mapping[n] = attr
                fields.append(n)

                if attr.index:
                    indexes.add((n, attr.index))

        for n in mapping:
            attrs.pop(n)

        attrs['__mapping__'] = mapping
        attrs['__indexes__'] = indexes

        return type.__new__(cls, name, bases, attrs)


class Document(_Document, metaclass=DocumentMetaClass):

    __logger__ = logging.getLogger(__name__)

    __connection__ = None
    __collection__ = None

    __after_save_hooks__ = [(log_modified_after_save, )]
    __before_save_hooks__ = [(validate_columns_before_save, )]

    __after_find_hooks__ = []
    __before_find_hooks__ = []

    __after_update_hooks__ = []
    __before_update_hooks__ = []

    __loop__ = None

    def __new__(cls, *args, **kwargs):
        if cls.__collection__:
            return super().__new__(cls, *args, **kwargs)
        connection = cls.__connection__
        database_name = connection.get_default_database().name

        collection_name = to_snake_case(cls.__name__)
        collection = connection \
            .get_database(database_name) \
            .get_collection(collection_name)
        codec_options = collection \
            .codec_options \
            ._replace(document_class=cls)

        cls.__collection__ = collection \
            .with_options(codec_options=codec_options)
        cls.__database_name__ = database_name
        cls.__collection_name__ = collection_name

        return super().__new__(cls, *args, **kwargs)

    @classmethod
    def set_event_loop(cls, loop):
        cls.__loop__ = loop

    @classmethod
    def set_connection(cls, connection, loop=None):
        cls.set_event_loop(loop or asyncio.get_event_loop())
        cls.__connection__ = connection

    @classmethod
    def set_application(cls, app):
        cls.__app__ = app

        @app.listener('before_server_start')
        def before_server_start(app, loop):
            from motor.motor_asyncio import AsyncIOMotorClient as MongoClient
            MONGO_URI = app.config.get('MONGO')
            cls.set_connection(MongoClient(MONGO_URI, io_loop=loop), loop)

        @app.listener('before_server_stop')
        def before_server_stop(app, loop):
            cls.__loop__ = None
            cls.__app__ = None
            cls.__connection__ = None

    @classmethod
    async def find_one(cls, *args, **kwargs):
        m = cls()
        await m._apply_before_hooks('find', *args, **kwargs)
        result = await cls.__collection__.find_one(*args, **kwargs)
        m._apply_after_hooks('find', result, *args, **kwargs)
        return result

    async def find_one(self, *args, **kwargs):  # noqa
        query, *args = args or (None, None)
        with_filter = True
        if not query:
            query = self
            with_filter = False
        await self._apply_before_hooks('find', query, *args, **kwargs)
        result = await self.__collection__.find_one(query, *args, **kwargs)
        self._apply_after_hooks('find', result, query, *args, **kwargs)
        if not result:
            raise DocumentNotFound(query)
        if with_filter:
            return result
        self.update(result)

    query = find_one

    @classmethod
    async def find(cls, *args, **kwargs):
        await cls._apply_before_hooks('find', *args, **kwargs)
        result = cls.__collection__.find(*args, **kwargs)
        cls._apply_after_hooks('find', result, *args, **kwargs)
        return result

    @classmethod
    async def update_one(cls, *args, **kwargs):
        query, *args = args or ({}, ())
        m = cls(query)
        await m._apply_before_hooks('update', m, args, kwargs)
        result = await m.__collection__.update_one(m, *args, **kwargs)
        if result.modified_count == 1 and result.upserted_id:
            doc = await m.__collection__ \
                .find_one({'_id': result.upserted_id})
        else:
            doc = await m.__collection__ \
                .find_one(m)
        m.update(doc)
        # TODO: if query is modified by upset, doc will be empty
        return m

    async def update_one(self, *args, **kwargs):  # noqa
        await self._apply_before_hooks('update', self, args, kwargs)
        result = await self.__collection__.update_one(self, *args, **kwargs)
        self._apply_after_hooks('update', result, self)
        return result

    async def save(self):
        await self._apply_before_hooks('save', self)
        if not self.get('_id'):
            insert_result = await self.__collection__.insert_one(self)
            self._id = insert_result.inserted_id
        else:
            await self.__collection__.update_one(
                {'_id': self._id},
                {'$set': self}
            )
        self._apply_after_hooks('save', self)
        return self

    @classmethod
    def register_before_hook(cls, act, *funcs):
        return getattr(cls, '__before_{act}_hooks__'.format(act=act)) \
            .extend(funcs)

    @classmethod
    def register_after_hook(cls, act, *funcs):
        return getattr(cls, '__after_{act}_hooks__'.format(act=act)) \
            .extend(funcs)

    @classmethod
    def before_save_hook(cls, *funcs):
        return cls.register_before_hook('save', *funcs)

    @classmethod
    def after_save_hook(cls, *funcs):
        return cls.register_after_hook('save', *funcs)

    @classmethod
    def before_update_hook(cls, *funcs):
        return cls.register_before_hook('update', *funcs)

    @classmethod
    def after_update_hook(cls, *funcs):
        return cls.register_after_hook('update', *funcs)

    @classmethod
    def before_find_hook(cls, *funcs):
        return cls.register_before_hook('find', *funcs)

    @classmethod
    def after_find_hook(cls, *funcs):
        return cls.register_after_hook('find', *funcs)

    @classmethod
    def _apply_after_hooks(
        cls,
        act,
        result,
        *query_args,
        **query_kwargs
    ):
        for hook, *hook_args in getattr(cls, '__after_{}_hooks__'.format(act)):
            if asyncio.iscoroutinefunction(hook):
                future = asyncio.ensure_future(
                    hook(hook_args, query_args, query_kwargs)
                )
                future.add_done_callback(cls._done)
            else:
                cls.__loop__ \
                    .call_soon_threadsafe(
                        hook,
                        result,
                        hook_args,
                        query_args,
                        query_kwargs
                    )
        return True

    @classmethod
    async def _apply_before_hooks(cls, act, *query_args, **query_kwargs):
        for hook, *args in getattr(cls, '__before_{}_hooks__'.format(act)):
            if asyncio.iscoroutinefunction(hook):
                await hook(args, query_args, query_kwargs)
            else:
                hook(args, query_args, query_kwargs)
        return True
