from aiogram.fsm.storage.base import BaseStorage, StorageKey, StateType
from aiogram.fsm.storage.redis import DefaultKeyBuilder
from typing import Optional, Dict, Any
import aiosqlite
import json
import ast


class AioSQLiteStorage(BaseStorage):
    async def start(self):
        connection = await aiosqlite.connect('fsm-storage')
        self.connection = connection
        try:
            await connection.execute('CREATE TABLE states (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, key TEXT NOT NULL, state TEXT NOT NULL, data TEXT NOT NULL)')
            await connection.commit()
        except aiosqlite.OperationalError:
            pass

    async def set_state(self, key: StorageKey, state: StateType = None) -> None:
        key_builder = DefaultKeyBuilder()
        key = key_builder.build(key, 'data')
        cursor = await self.connection.execute('SELECT state FROM states WHERE key = ?', (key,))
        result = await cursor.fetchone()
        if state is None:
            state = 'NONE'
        if not isinstance(state, str):
            state = state.state
        if result is not None:
            await self.connection.execute('UPDATE `states` SET `state` = ? WHERE `key` = ?', (state, key,))
        else:
            await self.connection.execute('INSERT INTO `states` (`key`, `state`, `data`) VALUES (?,?,?)', (key, state, '{}',))
        await self.connection.commit()
        await cursor.close()

    async def get_state(self, key: StorageKey) -> Optional[str]:
        key_builder = DefaultKeyBuilder()
        key = key_builder.build(key, 'data')
        cursor = await self.connection.execute('SELECT `state` FROM `states` WHERE `key` = ?', (key,))
        state = await cursor.fetchone()
        await cursor.close()
        if state is not None:
            if state[0] != 'NONE':
                return state[0]
        return None

    async def set_data(self, key: StorageKey, data: Dict[str, Any]) -> None:
        key_builder = DefaultKeyBuilder()
        key = key_builder.build(key, 'data')
        await self.connection.execute('UPDATE `states` SET `data` = ? WHERE `key` = ?', (json.dumps(data), key,))
        await self.connection.commit()

    async def get_data(self, key: StorageKey) -> Dict[str, Any]:
        key_builder = DefaultKeyBuilder()
        key = key_builder.build(key, 'data')
        cursor = await self.connection.execute('SELECT `data` FROM `states` WHERE `key` = ?', (key,))
        data = await cursor.fetchone()
        await cursor.close()
        return ast.literal_eval(data[0])

    async def update_data(self, key: StorageKey, data: Dict[str, Any]) -> Dict[str, Any]:
        current_data = await self.get_data(key=key)
        current_data.update(data)
        await self.set_data(key=key, data=current_data)
        return current_data.copy()

    async def close(self) -> None:
        await self.connection.close()