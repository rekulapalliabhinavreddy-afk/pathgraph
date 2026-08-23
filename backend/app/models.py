from typing import List, Optional
from pydantic import BaseModel, Field


class ProfileRequest(BaseModel):
    role_slug: str = Field(min_length=1, max_length=80)
    current_skills: List[str] = Field(default_factory=list, max_length=20)


class Role(BaseModel):
    slug: str
    name: str
    category: str
    description: str


class Skill(BaseModel):
    slug: str
    name: str
    category: str
