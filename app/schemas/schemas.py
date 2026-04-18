from pydantic import BaseModel


class RepoSchema(BaseModel):
    id: int
    name: str
    full_name: str
    private: bool


class RepoResponse(BaseModel):
    kind: str
    query: dict
    response: RepoSchema


class RepoListResponse(BaseModel):
    kind: str
    query: dict
    response: list[RepoSchema]
