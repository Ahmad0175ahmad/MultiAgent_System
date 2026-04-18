from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

from sqlmodel import SQLModel, Field, create_engine, Session, select

from config import settings  # ✅ Correct

logger = logging.getLogger(__name__)

#engine = create_engine(f"sqlite:///{SESSIONS_DB_PATH}", echo=False)
# Nai line
engine = create_engine(f"sqlite:///{settings.SESSIONS_DB_PATH}", echo=False)

class SessionModel(SQLModel, table=True):
    id: str = Field(primary_key=True)
    goal: str
    config: Optional[str] = None
    status: str = "pending"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    result: Optional[str] = None


def init_db():
    SQLModel.metadata.create_all(engine)


def create_session(session_id: str, goal: str, config: Optional[Dict[str, Any]] = None):
    try:
        with Session(engine) as db:
            session = SessionModel(
                id=session_id,
                goal=goal,
                config=str(config) if config else None,
                status="created"
            )
            db.add(session)
            db.commit()
            return session
    except Exception as e:
        logger.exception("Failed to create session")
        raise


def get_session(session_id: str) -> Optional[SessionModel]:
    try:
        with Session(engine) as db:
            return db.get(SessionModel, session_id)
    except Exception:
        logger.exception("Failed to fetch session")
        return None


def update_session(session_id: str, updates: Dict[str, Any]):
    try:
        with Session(engine) as db:
            session = db.get(SessionModel, session_id)
            if not session:
                return None

            for key, value in updates.items():
                setattr(session, key, value)

            db.add(session)
            db.commit()
            db.refresh(session)
            return session
    except Exception:
        logger.exception("Failed to update session")
        return None


def list_sessions() -> List[SessionModel]:
    try:
        with Session(engine) as db:
            statement = select(SessionModel)
            return db.exec(statement).all()
    except Exception:
        logger.exception("Failed to list sessions")
        return []
    
def delete_session(session_id: str) -> bool:
    try:
        with Session(engine) as db:
            session = db.get(SessionModel, session_id)
            if not session:
                return False
            db.delete(session)
            db.commit()
            return True
    except Exception:
        logger.exception("Failed to delete session")
        return False

def delete_all_sessions() -> bool:
    try:
        with Session(engine) as db:
            sessions = db.exec(select(SessionModel)).all()
            for session in sessions:
                db.delete(session)
            db.commit()
            return True
    except Exception:
        logger.exception("Failed to delete all sessions")
        return False