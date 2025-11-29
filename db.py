from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    create_engine,
)
from sqlalchemy.orm import sessionmaker, declarative_base
import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "agent.db"
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String(50), index=True)
    caption = Column(Text)
    status = Column(String(50), default="scheduled")  # scheduled, posted, error
    scheduled_time = Column(DateTime, nullable=True)
    posted_at = Column(DateTime, nullable=True)
    platform_post_id = Column(String(255), nullable=True)
    error = Column(Text, nullable=True)
    media_path = Column(String(255), nullable=True)
    branded_path = Column(String(255), nullable=True)


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    email = Column(String(255))
    phone = Column(String(50))
    service = Column(String(255))
    message = Column(Text)
    created_at = Column(
        DateTime, default=datetime.datetime.utcnow, nullable=False
    )


def init_db():
    Base.metadata.create_all(bind=engine)
