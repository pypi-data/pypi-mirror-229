import asyncio
import json
from typing import Callable, Dict, Any, List
from websockets.client import connect, WebSocketClientProtocol
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK
from .models.service import Service, ServiceInputParam
from .service_registry import ServiceRegistry
from .utils import logger

GATEWAY_URL = "wss://agentlabs.up.railway.app/ws/agent"


class Agent:
    """Agent class used to register services and deploy the agent on Weavel."""

    def __init__(self):
        self.service_registry = ServiceRegistry()

    def service(self, id: int, name: str, description: str):
        """Registers a service to the agent.
        Service id MUST be fetched from [Weavel](https://weavel.vercel.app) and specified.

        Args:
            - id (int): The id of the service. The service must be registered on Weavel and the id must be fetched from there.
            - name (str): The name of the service which will be provided to the agent. This is not for display purposes, but for the LLM agent to identify the service.
            - description (str): The description of the service which will be provided to the agent. This is not for display purposes, but for the LLM agent to identify the service.
        """

        def decorator(func: Callable):
            input_params: List[ServiceInputParam] = getattr(func, "input_params", [])
            self.service_registry.register(id, name, description, func, input_params)
            return func

        return decorator

    def service_input(
        self,
        name: str,
        display_name: str,
        description: str,
        type: str,
        required=True,
        choices=None,
    ):
        """Input parameter for a service.
        Input parameters are used to specify the arguments that the service accepts.

        Args:
            - name (str): The name of the input parameter. This is not for display purposes, but for the LLM agent to identify the input parameter.
            - display_name (str): This is the name that will be displayed to the user. If not specified, the name will be used.
            - description (str): The description of the input parameter. This is not for display purposes, but for the LLM agent to identify the input parameter.
            - required (bool): Whether the input parameter is required or not.
            - type (str): The type of the input parameter.
            - choices (List[Dict[str, Any]], optional): The available choices for the input. Defaults to None. If specified, only the choices will be accepted as input.

        """

        def decorator(func: Callable):
            if not hasattr(func, "input_params"):
                func.input_params = []
            param_data = ServiceInputParam(
                name=name,
                display_name=display_name,
                description=description,
                required=required,
                type=type,
                choices=choices if choices else [],
            )
            func.input_params.append(param_data)
            return func

        return decorator

    async def handle_message(
        self, message: Dict[str, Any], ws: WebSocketClientProtocol
    ):
        logger.info(f"Received message: {message}")
        try:
            if message["type"] == "LIST_SERVICES":
                response = self.service_registry.list()
            elif message["type"] == "GET_SERVICE_DETAILS":
                service_id = message["service_id"]
                response = self.service_registry.get_details(service_id)
            elif message["type"] == "RUN_SERVICE":
                service_id = message["service_id"]
                inputs = message["inputs"]
                service: Service = self.service_registry.get(service_id)
                if service:
                    if asyncio.iscoroutinefunction(service.func):
                        result = (
                            await service.func(**inputs)
                            if inputs
                            else await service.func()
                        )
                    else:
                        result = service.func(**inputs) if inputs else service.func()
                    response = {"result": result}
            # If the message has a correlation_id, add it to the response
            if message.get("correlation_id"):
                response["correlation_id"] = message["correlation_id"]
            await ws.send(json.dumps(response))
            logger.info(f"Sent response: {response}")
        except Exception as error:
            logger.error(f"Error handling message: {error}")
            await ws.send(str(error))

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
