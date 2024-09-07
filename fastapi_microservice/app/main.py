from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import crud, models, schemas, backend_client
from .database import engine, get_db
from .config import settings
import aioredis
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION)

@app.on_event("startup")
async def startup():
    redis = aioredis.from_url(settings.REDIS_URL,
                              encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")

@app.post("/comments/", response_model=schemas.Comment)
async def create_comment(comment: schemas.CommentCreate, db: Session = Depends(get_db)):
    task_exists = await backend_client.check_task_exists(comment.task_id)
    if not task_exists:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return crud.create_comment(db=db, comment=comment)

@app.get("/comments/", response_model=list[schemas.Comment])
@cache(expire=60)
async def read_comments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    comments = crud.get_comments(db, skip=skip, limit=limit)
    return comments

@app.get("/comments/{comment_id}", response_model=schemas.Comment)
@cache(expire=60)
async def read_comment(comment_id: int, db: Session = Depends(get_db)):
    db_comment = crud.get_comment(db, comment_id=comment_id)
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Комментарий не найден")
    return db_comment

@app.put("/comments/{comment_id}", response_model=schemas.Comment)
async def update_comment(comment_id: int, comment: schemas.CommentCreate, db: Session = Depends(get_db)):
    db_comment = crud.get_comment(db, comment_id=comment_id)
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Комментарий не найден")
    task_exists = await backend_client.check_task_exists(comment.task_id)
    if not task_exists:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return crud.update_comment(db, comment_id=comment_id, comment=comment)

@app.delete("/comments/{comment_id}", response_model=schemas.Comment)
async def delete_comment(comment_id: int, db: Session = Depends(get_db)):
    db_comment = crud.delete_comment(db, comment_id=comment_id)
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Комментарий не найден")
    return db_comment

@app.get("/tasks/{task_id}/comments", response_model=list[schemas.Comment])
@cache(expire=60)
async def read_task_comments(task_id: str, db: Session = Depends(get_db)):
    task_exists = await backend_client.check_task_exists(task_id)
    if not task_exists:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    comments = crud.get_comments_by_task(db, task_id=task_id)
    return comments