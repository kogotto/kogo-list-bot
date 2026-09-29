import asyncpg
import logging


class GoodType(asyncpg.Record):
    def id(self):
        return self['id']
    def name(self):
        return self['name']
    def created_at(self):
        return self['created_at']
    def is_active(self):
        return self['is_active']
    def username(self):
        return self['username']


class MyDB:

    def __init__(self, password: str):
        self.db_config = {
            "database": "kogotto",
            "user": "kogo_list_bot",
            "password": password,
            "host": '127.0.0.1',
        }

    async def _do_query(self, callback):
        conn = await asyncpg.connect(**self.db_config)
        try:
            return await callback(conn)
        except Exception as e:
            logging.error(f'Database error: {e}')
            raise
        finally:
            await conn.close()

    async def get_actual_goods(self):
        async def callback(conn: asyncpg.Connection):
            return await conn.fetch(
                'SELECT id, name, created_at, is_active, username FROM goods WHERE is_active;',
                record_class=GoodType
            )
        return await self._do_query(callback)

    async def insert_goods(self, goods, username):
        async def callback(conn: asyncpg.Connection):
            await conn.executemany(
                'INSERT INTO goods (name, username) VALUES ($1, $2)',
                (
                    (good, username) for good in goods
                )
            )
        await self._do_query(callback)

    async def buy_good(self, good_id: int):
        async def callback(conn: asyncpg.Connection):
            await conn.execute(
                'UPDATE goods SET is_active = false WHERE id = $1',
                good_id,
            )
        await self._do_query(callback)
