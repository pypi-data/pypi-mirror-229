from typing import Callable, List, Dict, Any, Optional
from pydantic import BaseModel


class ServiceInputParam(BaseModel):
    name: str
    display_name: str
    description: str
    required: bool
    type: str
    choices: Optional[List[Any]]


class Service(BaseModel):
    id: int
    name: str
    description: str
    func: Callable
    input_params: List[ServiceInputParam]
