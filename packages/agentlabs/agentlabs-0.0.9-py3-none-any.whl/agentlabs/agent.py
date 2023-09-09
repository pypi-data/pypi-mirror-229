import asyncio
import json
import inspect
from typing import Callable, Dict, Any, List
from websockets.client import connect, WebSocketClientProtocol
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK
from .models.service import Service, ServiceInputParam
from .service_registry import ServiceRegistry
from .utils import logger
from .utils.utils import internal_use
from .models.enums import Task, ServerTask, InputType

GATEWAY_URL = "wss://agentlabs.up.railway.app/ws/agent"


class Agent:
    """Agent class used to register services and deploy the agent on Weavel."""

    def __init__(self):
        self.service_registry = ServiceRegistry()
        self.ws: WebSocketClientProtocol = None

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
            if not hasattr(func, "runner_id"):
                func.runner_id = None

            return func

        return decorator

    def service_input(
        self,
        name: str,
        display_name: str,
        description: str,
        type: InputType,
        required=True,
        placeholder=None,
        options=None,
    ):
        """Input parameter for a service.
        Input parameters are used to specify the arguments that the service accepts.

        Args:
            - name (str): The name of the input parameter. This is not for display purposes, but for the LLM agent to identify the input parameter.
            - display_name (str): This is the name that will be displayed to the user. If not specified, the name will be used.
            - description (str): The description of the input parameter. This is not for display purposes, but for the LLM agent to identify the input parameter.
            - type (str): The type of the input parameter.
            - required (bool): Whether the input parameter is required or not.
            - placeholer (str): The placeholder that will be displayed to the user. Defaults to None.
            - options (List[Dict[str, Any]], optional): The available options for the input. Defaults to None. If specified, only the options will be accepted as input.

        """

        def decorator(func: Callable):
            if not hasattr(func, "input_params"):
                func.input_params = []
            param_data = ServiceInputParam(
                name=name,
                display_name=display_name,
                description=description,
                required=required,
                type=type.value,
                placeholder=placeholder if placeholder else "",
                options=options if options else [],
            )
            func.input_params.append(param_data)
            return func

        return decorator

    async def aupdate_status(self, status: str):
        """Updates the status of the agent on Weavel.
        The status will be displayed

        Args:
            - status (str): The status of the agent.
        """
        try:
            if self.ws:
                # Get the current frame and go one level up to the caller frame
                caller_frame = inspect.currentframe().f_back
                # Get the function that called this method
                caller_func = caller_frame.f_globals[caller_frame.f_code.co_name]

                runner_id = getattr(caller_func, "runner_id", None)
                if not runner_id:
                    logger.error(
                        f"Runner ID not found for function {caller_func.__name__}"
                    )
                    return
                message = {
                    "type": ServerTask.UPDATE_AGENT_STATUS.value,
                    "status": status,
                    "runner_id": runner_id,
                }
                await self.ws.send(message=json.dumps(message))
                logger.info(f"Requested agent status update: {message}")
            else:
                logger.error("Agent is not connected to the gateway.")
        except Exception as error:
            logger.error(f"Error updating agent status: {error}")

    def update_status(self, status: str):
        """Updates the status of the agent on Weavel.
        The status will be displayed

        Args:
            - status (str): The status of the agent.
        """
        asyncio.run(self.aupdate_status(status))

    @internal_use
    async def __handle_message(
        self, message: Dict[str, Any], ws: WebSocketClientProtocol
    ):
        logger.info(f"Received message: {message}")
        response: Dict[Any, str] = {}
        # If the message has a correlation_id, add it to the response
        if message.get("correlation_id"):
            response["correlation_id"] = message["correlation_id"]
        # If the message has a runner_id, add it to the response
        if message.get("runner_id"):
            response["runner_id"] = message["runner_id"]
        try:
            if message["type"] == Task.LIST_SERVICES:
                data = {"services": self.service_registry.list()}
            elif message["type"] == Task.GET_SERVICE_DETAILS:
                service_id = message["service_id"]
                data = self.service_registry.get_details(service_id)
            elif message["type"] == Task.RUN_SERVICE:
                service_id = message["service_id"]
                inputs = message["inputs"]
                service: Service = self.service_registry.get(service_id)
                if service:
                    if message.get("runner_id"):
                        service.func.runner_id = message["runner_id"]
                    else:
                        logger.error(
                            f"Runner ID not found in message: {message}. Cannot run service."
                        )
                        return
                    try:
                        await ws.send(
                            message=json.dumps(
                                {
                                    "type": ServerTask.UPDATE_SERVICE_STATUS.value,
                                    "status": "running",
                                    "runner_id": message["runner_id"],
                                }
                            )
                        )
                        logger.info(f"Started service: {service.name}")
                        if asyncio.iscoroutinefunction(service.func):
                            outputs = (
                                await service.func(**inputs)
                                if inputs
                                else await service.func()
                            )
                        else:
                            outputs = (
                                service.func(**inputs) if inputs else service.func()
                            )
                        data = {
                            "type": ServerTask.UPDATE_SERVICE_OUTPUTS.value,
                            "outputs": outputs,
                            "status": "completed",
                        }
                    except Exception as error:
                        data = {
                            "type": ServerTask.UPDATE_SERVICE_OUTPUTS.value,
                            "outputs": None,
                            "status": "failed",
                            "log": str(error),
                        }
            response.update(data)
            await ws.send(json.dumps(response))
            logger.info(f"Sent response: {response}")
        except Exception as error:
            logger.error(f"Error handling message: {error}")
            await ws.send(str(error))

    @internal_use
    async def __connect_to_gateway(
        self, token: str, retries=12 * 24, retry_delay=5 * 60
    ):
        headers = {"Authorization": f"Bearer {token}"}
        for _ in range(retries):
            try:
                async with connect(
                    GATEWAY_URL,
                    extra_headers=headers,
                    # ping_interval=10,
                    # ping_timeout=1,
                    # timeout=3600 * 24,  # Timeout is set to 24 hours
                ) as ws:
                    logger.success("Connected to gateway. Your agent is now online! 🎉")
                    self.ws = ws
                    while True:
                        message = await ws.recv()
                        data = json.loads(message)
                        await self.__handle_message(data, ws)
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
        # TODO: Validate specified service IDs with agent token
        loop.run_until_complete(self.__connect_to_gateway(token))
