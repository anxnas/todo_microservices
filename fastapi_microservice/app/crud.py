from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional
from . import models, schemas
from log_config import get_logger

logger = get_logger("crud")

class CommentCRUD:
    def get_comment(self, db: Session, comment_id: int) -> Optional[models.Comment]:
        """
        Получает комментарий по его ID.

        Args:
            db (Session): Сессия базы данных.
            comment_id (int): ID комментария.

        Returns:
            Optional[models.Comment]: Объект комментария или None, если не найден.
        """
        try:
            comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
            if comment:
                logger.info(f"Получен комментарий с ID {comment_id}")
            else:
                logger.warning(f"Комментарий с ID {comment_id} не найден")
            return comment
        except SQLAlchemyError as e:
            logger.log_exception(f"Ошибка при получении комментария с ID {comment_id}: {str(e)}")

    def get_comments(self, db: Session, skip: int = 0, limit: int = 100) -> List[models.Comment]:
        """
        Получает список комментариев с пагинацией.

        Args:
            db (Session): Сессия базы данных.
            skip (int): Количество пропускаемых записей.
            limit (int): Максимальное количество возвращаемых записей.

        Returns:
            List[models.Comment]: Список объектов комментариев.
        """
        try:
            comments = db.query(models.Comment).offset(skip).limit(limit).all()
            logger.info(f"Получено {len(comments)} комментариев")
            return comments
        except SQLAlchemyError as e:
            logger.log_exception(f"Ошибка при получении списка комментариев: {str(e)}")

    def get_comments_by_task(self, db: Session, task_id: int) -> List[models.Comment]:
        """
        Получает все комментарии для заданной задачи.

        Args:
            db (Session): Сессия базы данных.
            task_id (int): ID задачи.

        Returns:
            List[models.Comment]: Список объектов комментариев для заданной задачи.
        """
        try:
            comments = db.query(models.Comment).filter(models.Comment.task_id == task_id).all()
            logger.info(f"Получено {len(comments)} комментариев для задачи с ID {task_id}")
            return comments
        except SQLAlchemyError as e:
            logger.log_exception(f"Ошибка при получении комментариев для задачи с ID {task_id}: {str(e)}")

    def create_comment(self, db: Session, comment: schemas.CommentCreate) -> models.Comment:
        """
        Создает новый комментарий.

        Args:
            db (Session): Сессия базы данных.
            comment (schemas.CommentCreate): Данные для создания комментария.

        Returns:
            models.Comment: Созданный объект комментария.
        """
        try:
            db_comment = models.Comment(**comment.dict())
            db.add(db_comment)
            db.commit()
            db.refresh(db_comment)
            logger.info(f"Создан новый комментарий с ID {db_comment.id}")
            return db_comment
        except SQLAlchemyError as e:
            db.rollback()
            logger.log_exception(f"Ошибка при создании комментария: {str(e)}")

    def update_comment(self, db: Session, comment_id: int, comment: schemas.CommentCreate) -> Optional[models.Comment]:
        """
        Обновляет существующий комментарий.

        Args:
            db (Session): Сессия базы данных.
            comment_id (int): ID обновляемого комментария.
            comment (schemas.CommentCreate): Новые данные комментария.

        Returns:
            Optional[models.Comment]: Обновленный объект комментария или None, если комментарий не найден.
        """
        try:
            db_comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
            if db_comment:
                for key, value in comment.dict().items():
                    setattr(db_comment, key, value)
                db.commit()
                db.refresh(db_comment)
                logger.info(f"Обновлен комментарий с ID {comment_id}")
            else:
                logger.warning(f"Попытка обновить несуществующий комментарий с ID {comment_id}")
            return db_comment
        except SQLAlchemyError as e:
            db.rollback()
            logger.log_exception(f"Ошибка при обновлении комментария с ID {comment_id}: {str(e)}")

    def delete_comment(self, db: Session, comment_id: int) -> Optional[models.Comment]:
        """
        Удаляет комментарий.

        Args:
            db (Session): Сессия базы данных.
            comment_id (int): ID удаляемого комментария.

        Returns:
            Optional[models.Comment]: Удаленный объект комментария или None, если комментарий не найден.
        """
        try:
            db_comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
            if db_comment:
                db.delete(db_comment)
                db.commit()
                logger.info(f"Удален комментарий с ID {comment_id}")
            else:
                logger.warning(f"Попытка удалить несуществующий комментарий с ID {comment_id}")
            return db_comment
        except SQLAlchemyError as e:
            db.rollback()
            logger.log_exception(f"Ошибка при удалении комментария с ID {comment_id}: {str(e)}")
