from asyncio import TimeoutError
import logging

from aio_pika.abc import AbstractExchange, AbstractMessage, AbstractChannel, AbstractConnection
from aio_pika.exceptions import DeliveryError
from aio_pika import connect
from config import settings


logger = logging.getLogger('producer ' + __name__)

connection: AbstractConnection = None

async def get_connection() -> AbstractConnection:
    global connection
    if not connection:
        connection = await connect(settings.rabbitmq.connection)
    return connection


async def close_connection() -> None:
    global connection
    if isinstance(connection, AbstractConnection):
        await connection.close()

async def get_channel() -> AbstractChannel:
    conn = await get_connection()
    return await conn.channel(publisher_confirms=True, 
                              on_return_raises=True)


async def publish_with_retries(exchanger: AbstractExchange, 
                               queue_name: str, 
                               message: AbstractMessage, 
                               retries: int = 5):
    for i in range(retries):
        try:
            await exchanger.publish(message=message,
                                              routing_key=queue_name,
                                              timeout=10)
            break
        except DeliveryError as e:
            logger.error('ошибка отправки сообщения: %s', e)
        except TimeoutError as e:
            logger.error('Вышло время ожидания подтверждения доставки сообщения брокером')
            break