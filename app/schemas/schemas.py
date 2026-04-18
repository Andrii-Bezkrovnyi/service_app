from pydantic import BaseModel
from typing import List, Dict, Any

class RepoSchema(BaseModel):
    id: int
    name: str
    full_name: str
    private: bool

class RepoResponse(BaseModel):
    kind: str
    query: Dict[str, Any]
    response: RepoSchema

class RepoListResponse(BaseModel):
    kind: str
    query: Dict[str, Any]
    response: List[RepoSchema]

