import dataclasses
import json
from dataclasses import dataclass
from enum import Enum

import aio_pika
from aio_pika import DeliveryMode


class AckType(str, Enum):
    ACK = "ack"
    NACK_REQUEUE = "nack_requeue"
    NACK_DISCARD = "nack_discard"


@dataclass
class PubSubContext:
    key: str
    exchange: str
    queue_name: str


async def _declare_and_bind(
    channel: aio_pika.Channel,
    ctx: PubSubContext,
) -> aio_pika.Queue:
    return await channel.declare_queue(name=ctx.queue_name, passive=True)


## ------------- UTILITY FOR SUBSCRIBE FEATURE ---------------- ##

# async def subscribe(
#     connection_string: str,
#     ctx: PubSubContext,
#     handler: Callable,
#     deserialize_func: Callable = json.loads,
# ) -> asyncio.Task:
#     async def run_consumer():
#         conn = await get_connection(connection_string)
#         channel = await conn.channel()
#         await channel.set_qos(prefetch_count=10)
#         queue = await _declare_and_bind(channel, ctx)

#         async with queue.iterator() as q_iter:
#             async for message in q_iter:
#                 data = deserialize_func(message.body)
#                 ack_type = await handler(data)
#                 if ack_type == AckType.ACK:
#                     await message.ack()
#                 elif ack_type == AckType.NACK_REQUEUE:
#                     await message.reject(requeue=True)
#                 elif ack_type == AckType.NACK_DISCARD:
#                     await message.reject(requeue=False)

#     return asyncio.create_task(run_consumer())


async def publish_json(channel: aio_pika.Channel, exchange: str, key: str, val):
    if dataclasses.is_dataclass(val):
        val = dataclasses.asdict(val)

    message = aio_pika.Message(
        body=json.dumps(val).encode(),
        content_type="application/json",
        delivery_mode=DeliveryMode.PERSISTENT,
    )

    exchange_obj = await channel.get_exchange(exchange)
    await exchange_obj.publish(message, routing_key=key)


async def get_connection(
    connection_string: str,
) -> aio_pika.RobustConnection:
    return await aio_pika.connect_robust(url=connection_string)
