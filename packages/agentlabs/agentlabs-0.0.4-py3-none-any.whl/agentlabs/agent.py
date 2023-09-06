import asyncio
import json
from typing import Callable, Dict, Any
from websockets.client import connect, WebSocketClientProtocol
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK
from .service_registry import ServiceRegistry, Service
from .utils import logger

GATEWAY_URL = "wss://agentlabs.up.railway.app/ws/agent"


class Agent:
    """Agent class used to register services and deploy the agent on Weavel."""

    def __init__(self):
        self.service_registry = ServiceRegistry()

    def service(self, name: str, description: str):
        def decorator(func: Callable):
            self.service_registry.register(name, description, func)
            return func

        return decorator

    async def handle_message(
        self, message: Dict[str, Any], ws: WebSocketClientProtocol
    ):
        logger.info(f"Received message: {message}")
        try:
            if message["type"] == "LIST_SERVICES":
                response = self.service_registry.list()
            elif message["type"] == "RUN_SERVICE":
                service_name = message["service_name"]
                args = message["args"]
                service: Service = self.service_registry.get(service_name)
                if service:
                    result = await service.func(**args)
                    response = {"result": result}
            await ws.send(json.dumps(response))
            logger.info(f"Sent response: {response}")
        except Exception as error:
            logger.error(f"Error handling message: {error}")

    async def connect_to_gateway(self, token: str):
        headers = {"Authorization": f"Bearer {token}"}
        while True:
            try:
                async with connect(GATEWAY_URL, extra_headers=headers) as ws:
                    logger.success("Connected to gateway. Your agent is now online! 🎉")
                    while True:
                        try:
                            message = await ws.recv()
                            data = json.loads(message)
                            await self.handle_message(data, ws)
                        except Exception as error:
                            logger.error(f"Error receiving message: {error}")
            except Exception as error:
                asyncio.sleep(60 * 5)
                logger.error(f"Error connecting to gateway: {error}")

    async def connect_to_gateway(self, token: str, retries=12 * 24, retry_delay=5 * 60):
        headers = {"Authorization": f"Bearer {token}"}
        for _ in range(retries):
            try:
                async with connect(
                    GATEWAY_URL, extra_headers=headers, timeout=30
                ) as ws:  # Increased timeout to 30 seconds
                    logger.success("Connected to gateway. Your agent is now online! 🎉")
                    while True:
                        message = await ws.recv()
                        data = json.loads(message)
                        await self.handle_message(data, ws)
            except (ConnectionClosedError, ConnectionClosedOK):
                # If the connection was closed gracefully, handle it accordingly
                logger.warning("Connection to the gateway was closed.")
            except TimeoutError:
                logger.error(
                    f"Timeout error while connecting to the gateway. Retrying in {retry_delay} seconds..."
                )
                await asyncio.sleep(retry_delay)
            except Exception as error:
                logger.error(f"Error receiving message: {error}")

    def run(self, token: str):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.connect_to_gateway(token))
