from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
DB_USER = "root"
DB_PASSWORD = "Arun%401493"
DB_HOST = "localhost"
DB_PORT = "3306"
DB_NAME = "flight_book"
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()