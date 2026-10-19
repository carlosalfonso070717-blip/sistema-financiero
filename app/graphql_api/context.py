from fastapi import Depends, Request
from sqlalchemy.orm import Session
from strawberry.fastapi import BaseContext

from app.database import get_session


class Context(BaseContext):
    def __init__(self, db: Session, request: Request):
        super().__init__()
        self.db = db
        self.request = request


async def get_context(request: Request, db: Session = Depends(get_session)) -> Context:
    return Context(db=db, request=request)
