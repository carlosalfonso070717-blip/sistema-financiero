"""Contexto de GraphQL: sesion de base de datos.
"""
from fastapi import Depends
from sqlalchemy.orm import Session
from strawberry.fastapi import BaseContext

from app.database import get_session


class Context(BaseContext):
    """Se inyecta en cada resolver y se lee con info.context."""

    def __init__(self, db: Session):
        super().__init__()
        self.db = db


async def get_context(db: Session = Depends(get_session)) -> Context:
    return Context(db=db)
