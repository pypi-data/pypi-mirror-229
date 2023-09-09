from typing import Any, Callable, Dict, List
from .registry import Registry
from .models.service import Service, ServiceInputParam


class ServiceRegistry(Registry):
    def __init__(self):
        self.services: Dict[int, Service] = {}

    def register(
        self,
        id: int,
        name: str,
        description: str,
        func: Callable,
        input_params: List[ServiceInputParam] = [],
    ) -> None:
        service = Service(
            id=id,
            name=name,
            description=description,
            func=func,
            input_params=input_params,
        )
        self.services[id] = service

    def get(self, id: int) -> Service:
        return self.services.get(id)

    def get_details(self, id: int):
        print(self.services)
        service = self.services.get(id)
        return {
            "id": service.id,
            "name": service.name,
            "description": service.description,
            "input_params": [
                {
                    "name": param.name,
                    "display_name": param.display_name,
                    "description": param.description,
                    "required": param.required,
                    "type": param.type,
                    "choices": param.choices,
                }
                for param in service.input_params
            ],
        }

    def list(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": service.id,
                "name": service.name,
                "description": service.description,
                "input_params": [
                    {
                        "name": param.name,
                        "description": param.description,
                        "required": param.required,
                        "type": param.type,
                        "choices": param.choices,
                    }
                    for param in service.input_params
                ],
            }
            for service in self.services.values()
        ]
