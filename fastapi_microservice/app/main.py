from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from . import models, schemas
from .database import engine, get_db
from .config import settings
from .crud import CommentCRUD
from .backend_client import BackendClient
from .log_config import get_logger
import aioredis
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache

logger = get_logger("main")

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION)

comment_crud = CommentCRUD()
backend_client = BackendClient()

@app.on_event("startup")
async def startup() -> None:
    """
    Инициализация кэша Redis при запуске приложения.
    """
    try:
        redis = aioredis.from_url(settings.REDIS_URL,
                                  encoding="utf8", decode_responses=True)
        FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
        logger.info("Кэш Redis успешно инициализирован")
    except Exception as e:
        logger.log_exception(f"Ошибка при инициализации кэша Redis: {str(e)}")
        raise

@app.post("/comments/", response_model=schemas.Comment)
async def create_comment(comment: schemas.CommentCreate, db: Session = Depends(get_db)) -> schemas.Comment:
    """
    Создает новый комментарий.

    Args:
        comment (schemas.CommentCreate): Данные для создания комментария.
        db (Session): Сессия базы данных.

    Returns:
        schemas.Comment: Созданный комментарий.

    Raises:
        HTTPException: Если задача не найдена или произошла ошибка при создании комментария.
    """
    try:
        task_exists: bool = await backend_client.check_task_exists(comment.task_id)
        if not task_exists:
            logger.warning(f"Попытка создать комментарий для несуществующей задачи {comment.task_id}")
            raise HTTPException(status_code=404, detail="Задача не найдена")
        new_comment = comment_crud.create_comment(db=db, comment=comment)
        logger.info(f"Создан новый комментарий с ID {new_comment.id}")
        return new_comment
    except Exception as e:
        logger.log_exception(f"Ошибка при создании комментария: {str(e)}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

@app.get("/comments/", response_model=List[schemas.Comment])
@cache(expire=60)
async def read_comments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)) -> List[schemas.Comment]:
    """
    Получает список комментариев с пагинацией.

    Args:
        skip (int): Количество пропускаемых записей.
        limit (int): Максимальное количество возвращаемых записей.
        db (Session): Сессия базы данных.

    Returns:
        List[schemas.Comment]: Список комментариев.
    """
    try:
        comments: List[schemas.Comment] = comment_crud.get_comments(db, skip=skip, limit=limit)
        logger.info(f"Получено {len(comments)} комментариев")
        return comments
    except Exception as e:
        logger.log_exception(f"Ошибка при получении списка комментариев: {str(e)}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

@app.get("/comments/{comment_id}", response_model=schemas.Comment)
@cache(expire=60)
async def read_comment(comment_id: int, db: Session = Depends(get_db)) -> schemas.Comment:
    """
    Получает комментарий по его ID.

    Args:
        comment_id (int): ID комментария.
        db (Session): Сессия базы данных.

    Returns:
        schemas.Comment: Комментарий.

    Raises:
        HTTPException: Если комментарий не найден.
    """
    try:
        db_comment = comment_crud.get_comment(db, comment_id=comment_id)
        if db_comment is None:
            logger.warning(f"Попытка получить несуществующий комментарий с ID {comment_id}")
            raise HTTPException(status_code=404, detail="Комментарий не найден")
        logger.info(f"Получен комментарий с ID {comment_id}")
        return db_comment
    except Exception as e:
        logger.log_exception(f"Ошибка при получении комментария с ID {comment_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

@app.put("/comments/{comment_id}", response_model=schemas.Comment)
async def update_comment(comment_id: int, comment: schemas.CommentCreate, db: Session = Depends(get_db)) -> schemas.Comment:
    """
    Обновляет существующий комментарий.

    Args:
        comment_id (int): ID обновляемого комментария.
        comment (schemas.CommentCreate): Новые данные комментария.
        db (Session): Сессия базы данных.

    Returns:
        schemas.Comment: Обновленный комментарий.

    Raises:
        HTTPException: Если комментарий не найден или задача не существует.
    """
    try:
        db_comment = comment_crud.get_comment(db, comment_id=comment_id)
        if db_comment is None:
            logger.warning(f"Попытка обновить несуществующий комментарий с ID {comment_id}")
            raise HTTPException(status_code=404, detail="Комментарий не найден")
        task_exists = await backend_client.check_task_exists(comment.task_id)
        if not task_exists:
            logger.warning(f"Попытка обновить комментарий для несуществующей задачи {comment.task_id}")
            raise HTTPException(status_code=404, detail="Задача не найдена")
        updated_comment = comment_crud.update_comment(db, comment_id=comment_id, comment=comment)
        logger.info(f"Обновлен комментарий с ID {comment_id}")
        return updated_comment
    except Exception as e:
        logger.log_exception(f"Ошибка при обновлении комментария с ID {comment_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

@app.delete("/comments/{comment_id}", response_model=schemas.Comment)
async def delete_comment(comment_id: int, db: Session = Depends(get_db)) -> schemas.Comment:
    """
    Удаляет комментарий.

    Args:
        comment_id (int): ID удаляемого комментария.
        db (Session): Сессия базы данных.

    Returns:
        schemas.Comment: Удаленный комментарий.

    Raises:
        HTTPException: Если комментарий не найден.
    """
    try:
        db_comment = comment_crud.delete_comment(db, comment_id=comment_id)
        if db_comment is None:
            logger.warning(f"Попытка удалить несуществующий комментарий с ID {comment_id}")
            raise HTTPException(status_code=404, detail="Комментарий не найден")
        logger.info(f"Удален комментарий с ID {comment_id}")
        return db_comment
    except Exception as e:
        logger.log_exception(f"Ошибка при удалении комментария с ID {comment_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

@app.get("/tasks/{task_id}/comments", response_model=List[schemas.Comment])
@cache(expire=60)
async def read_task_comments(task_id: int, db: Session = Depends(get_db)) -> List[schemas.Comment]:
    """
    Получает все комментарии для заданной задачи.

    Args:
        task_id (int): ID задачи.
        db (Session): Сессия базы данных.

    Returns:
        List[schemas.Comment]: Список комментариев для заданной задачи.

    Raises:
        HTTPException: Если задача не найдена.
    """
    try:
        task_exists: bool = await backend_client.check_task_exists(task_id)
        if not task_exists:
            logger.warning(f"Попытка получить комментарии для несуществующей задачи с ID {task_id}")
            raise HTTPException(status_code=404, detail="Задача не найдена")
        comments = comment_crud.get_comments_by_task(db, task_id=task_id)
        logger.info(f"Получено {len(comments)} комментариев для задачи с ID {task_id}")
        return comments
    except Exception as e:
        logger.log_exception(f"Ошибка при получении комментариев для задачи с ID {task_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")