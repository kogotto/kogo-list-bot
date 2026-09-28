import psycopg2
from dataclasses import dataclass
from datetime import datetime


@dataclass
class DbRow:
    id: int
    name: str
    created_at: datetime
    is_active: bool
    username: str



class MyDB:

    def __init__(self, password: str):
        self.db_config = {
            "dbname": "kogotto",
            "user": "kogo_list_bot",
            "password": password,
            "host": '127.0.0.1',
        }

    async def _do_query(self, callback):
        try:
            with psycopg2.connect(**self.db_config) as conn:
                with conn.cursor() as cur:
                    return callback(cur)
        except psycopg2.Error as e:
            print(f'Database error: {e}')

    async def get_actual_goods(self):
        def callback(cur):
            cur.execute('SELECT * FROM goods WHERE is_active;')
            return [
                DbRow(
                    id=row[0],
                    name=row[1],
                    created_at=row[2],
                    is_active=row[3],
                    username=row[4],
                ) for row in cur.fetchall()
            ]
        return await self._do_query(callback)

    async def insert_goods(self, goods, username):
        def callback(cur):
            for good in goods:
                cur.execute(
                    'INSERT INTO goods (name, username) VALUES (%s, %s)',
                    (good, username),
                )
        return await self._do_query(callback)

    async def delete_good(self, good_id: int):
        def callback(cur):
            cur.execute(
                'UPDATE goods SET is_active = false WHERE id = %s',
                (good_id,),
            )
        return await self._do_query(callback)

