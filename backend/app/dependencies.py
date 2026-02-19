from fastapi import Request
import aio_pika


def get_rmq_channel(request: Request) -> aio_pika.RobustChannel:
    return request.app.state.rmq_channel
