from pydantic import BaseModel


class WorkspaceSummary(BaseModel):
    id: str
    name: str
    role: str
