from fastapi import Depends, Request
from sqlalchemy.orm import Session
from strawberry.fastapi import BaseContext

from app.core.security import decode_access_token
from app.database import get_session
from app.models import User


class Context(BaseContext):
    def __init__(self, db: Session, user: User | None):
        super().__init__()
        self.db = db
        self.user = user


async def get_context(request: Request, db: Session = Depends(get_session)) -> Context:
    user = None
    header = request.headers.get("Authorization", "")
    if header.lower().startswith("bearer "):
        user_id = decode_access_token(header.split(" ", 1)[1].strip())
        if user_id:
            user = db.get(User, user_id)
    return Context(db=db, user=user)
