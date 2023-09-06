from .registry import Registry
from typing import Callable, List, Dict, Any
from pydantic import BaseModel


class Service(BaseModel):
    name: str
    description: str
    func: Callable


class ServiceRegistry(Registry):
    def __init__(self):
        self.services: Dict[str, Service] = {}

    def register(self, name: str, description: str, func: Callable) -> None:
        service = Service(name=name, description=description, func=func)
        self.services[name] = service

    def get(self, name: str) -> Service:
        return self.services.get(name)

    def list(self) -> List[Dict[str, Any]]:
        return [
            {"name": service.name, "description": service.description}
            for service in self.services.values()
        ]
