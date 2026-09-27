import psycopg2


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
            cur.execute('SELECT name FROM goods WHERE is_active;')
            return cur.fetchall()
        return await self._do_query(callback)

    async def insert_goods(self, goods, username):
        def callback(cur):
            for good in goods:
                cur.execute(
                    'INSERT INTO goods (name, username) VALUES (%s, %s)',
                    (good, username),
                )
        return await self._do_query(callback)

