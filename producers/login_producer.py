import aio_pika
from aio_pika import DeliveryMode, ExchangeType
from pydantic import BaseModel, EmailStr

from config import settings
from .utils import get_channel, publish_with_retries




class LoginMessage(BaseModel):
    username: EmailStr
    scopes: str


async def publish(username: str, scopes: str):
    body = LoginMessage(username=username, scopes=scopes).model_dump_json().encode(encoding='utf-8')
    message = aio_pika.Message(body=body, 
                               delivery_mode=DeliveryMode.PERSISTENT,
                               expiration=settings.rabbitmq.message_ttl,
                               content_type='application/json',
                               content_encoding='utf-8')
    channel = await get_channel()
    async with channel:
        exchage = await channel.declare_exchange('login_exchange', 
                                         type=ExchangeType.DIRECT)
        if settings.test_mode:
            queue = await channel.declare_queue(settings.test_rabbitmq.login_queue, 
                                      durable=True)
        else:
            queue = await channel.declare_queue(settings.rabbitmq.login_queue, 
                                      durable=True)
        await queue.bind(exchange=exchage, 
                   routing_key=queue.name)
        await publish_with_retries(exchage, queue.name, message)