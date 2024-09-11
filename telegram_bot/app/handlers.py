from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.input import MessageInput
from services.api import api_service
from utils.localization import localization
from typing import List, Dict, Any, Optional
from aiogram.types import CallbackQuery, Message
from config import config
from states import MainSG

logger = config.LOGGER.get_logger(__name__)

async def on_task_selected(c: CallbackQuery, widget: Any, manager: DialogManager, item_id: str) -> None:
    """
    Обработчик выбора задачи.

    Args:
        c (CallbackQuery): Объект обратного вызова.
        widget (Any): Виджет, вызвавший обработчик.
        manager (DialogManager): Менеджер диалога.
        item_id (str): ID выбранной задачи.

    Returns:
        None
    """
    try:
        logger.info(f"Выбрана задача с ID: {item_id}")
        manager.dialog_data["selected_task_id"] = str(item_id)
        await manager.switch_to(MainSG.task_details)
        logger.info(f"Переключение на детали задачи для ID: {item_id}")
    except Exception as e:
        logger.log_exception(f"Ошибка при выборе задачи с ID {item_id}")
        await c.answer("Произошла ошибка при выборе задачи. Попробуйте еще раз.")

async def on_language_selected(c: CallbackQuery, select: Any, manager: DialogManager) -> None:
    """
    Обработчик выбора языка.

    Args:
        c (CallbackQuery): Объект обратного вызова.
        select (Any): Виджет выбора.
        manager (DialogManager): Менеджер диалога.

    Returns:
        None
    """
    try:
        language: str = select.item_id
        user = manager.event.from_user
        logger.info(f"Пользователь {user.id} выбрал язык: {language}")
        await localization.set_user_locale(user.id, language)
        await manager.switch_to(MainSG.main)
        logger.info(f"Язык установлен для пользователя {user.id}: {language}")
    except Exception as e:
        logger.log_exception(f"Ошибка при выборе языка {language} для пользователя {user.id}", exc_info=True)
        await c.answer("Произошла ошибка при выборе языка. Попробуйте еще раз.")

async def on_delete_comment(c: CallbackQuery, widget: Button, manager: DialogManager, item_id: str) -> None:
    """
    Обработчик удаления комментария.

    Args:
        c (CallbackQuery): Объект обратного вызова.
        widget (Button): Виджет кнопки.
        manager (DialogManager): Менеджер диалога.
        item_id (str): ID комментария для удаления.

    Returns:
        None
    """
    try:
        user_token: str = manager.dialog_data.get("user_token")
        logger.info(f"Попытка удаления комментария с ID: {item_id}")
        success: bool = await api_service.delete_comment(user_token, item_id)
        locale: str = manager.dialog_data.get("locale", "ru")

        if success:
            text: str = localization.get_text("comment_deleted", locale)
            logger.info(f"Комментарий с ID {item_id} успешно удален")
        else:
            text: str = localization.get_text("error_deleting_comment", locale)
            logger.warning(f"Не удалось удалить комментарий с ID {item_id}")

        task_id: str = manager.dialog_data.get("selected_task_id")
        comments: List[Dict[str, Any]] = await api_service.get_comments(user_token, task_id)

        await manager.update({
            "comments_list": comments,
            "comments": "\n\n".join([
                f"ID: {comment['id']}\nСодержание: {comment['content']}"
                for comment in comments
            ])
        })

        await c.answer(text)

        return await manager.switch_to(MainSG.comments)
    except Exception as e:
        logger.log_exception(f"Ошибка при удалении комментария с ID {item_id}")
        await c.answer("Произошла ошибка при удалении комментария. Попробуйте еще раз.")


async def on_category_del(c: CallbackQuery, widget: Button, manager: DialogManager, item_id: str) -> None:
    """
    Обработчик удаления категории.

    Args:
        c (CallbackQuery): Объект обратного вызова.
        widget (Button): Виджет кнопки.
        manager (DialogManager): Менеджер диалога.
        item_id (str): ID категории для удаления.

    Returns:
        None
    """
    try:
        user_token: str = manager.dialog_data.get("user_token")
        logger.info(f"Попытка удаления категории с ID: {item_id}")
        success: bool = await api_service.delete_category(user_token, item_id)
        locale: str = manager.dialog_data.get("locale", "ru")

        if success:
            text: str = localization.get_text("category_deleted", locale)
            logger.info(f"Категория с ID {item_id} успешно удалена")
        else:
            text: str = localization.get_text("error_deleting_category", locale)
            logger.warning(f"Не удалось удалить категорию с ID {item_id}")

        await c.answer(text, show_alert=True)
        await manager.update({"categories": await api_service.get_categories(user_token)})
    except Exception as e:
        logger.log_exception(f"Ошибка при удалении категории с ID {item_id}")
        await c.answer("Произошла ошибка при удалении категории. Попробуйте еще раз.")

async def on_category_selected(c: CallbackQuery, widget: Button, manager: DialogManager, item_id: str) -> None:
    """
    Обработчик выбора категории.

    Args:
        c (CallbackQuery): Объект обратного вызова.
        widget (Button): Виджет кнопки.
        manager (DialogManager): Менеджер диалога.
        item_id (str): ID выбранной категории.

    Returns:
        None
    """
    try:
        selected_categories: List[Dict[str, str]] = manager.dialog_data.get("selected_categories", [])
        all_categories: List[Dict[str, Any]] = manager.dialog_data.get("all_categories", [])

        category: Optional[Dict[str, Any]] = next((cat for cat in all_categories if cat['id'] == item_id), None)

        if category:
            existing_category: Optional[Dict[str, str]] = next((cat for cat in selected_categories if cat['id'] == item_id), None)
            if existing_category:
                selected_categories.remove(existing_category)
                await c.answer("❌")
                logger.info(f"Категория с ID {item_id} удалена из выбранных")
            else:
                selected_categories.append({'name': category['name'], 'id': category['id']})
                await c.answer("✅")
                logger.info(f"Категория с ID {item_id} добавлена в выбранные")
            manager.dialog_data["selected_categories"] = selected_categories
    except Exception as e:
        logger.log_exception(f"Ошибка при выборе категории с ID {item_id}")
        await c.answer("Произошла ошибка при выборе категории. Попробуйте еще раз.")

async def on_save_categories(c: CallbackQuery, widget: Button, manager: DialogManager) -> None:
    """
    Обработчик сохранения выбранных категорий.

    Args:
        c (CallbackQuery): Объект обратного вызова.
        widget (Button): Виджет кнопки.
        manager (DialogManager): Менеджер диалога.

    Returns:
        None
    """
    try:
        user_token: str = manager.dialog_data.get("user_token")
        task_id: str = manager.dialog_data.get("selected_task_id")
        locale: str = manager.dialog_data.get("locale", "ru")
        selected_categories: List[Dict[str, str]] = manager.dialog_data.get("selected_categories", [])
        logger.info(f"Попытка сохранения категорий для задачи с ID: {task_id}")
        success: bool = await api_service.update_task_categories(user_token, task_id, selected_categories)
        if success:
            await manager.event.answer(localization.get_text("categories_updated", locale))
            logger.info(f"Категории успешно обновлены для задачи с ID {task_id}")
        else:
            await manager.event.answer(localization.get_text("error_updating_categories", locale))
            logger.warning(f"Не удалось обновить категории для задачи с ID {task_id}")
        await manager.switch_to(MainSG.task_details)
    except Exception as e:
        logger.log_exception(f"Ошибка при сохранении категорий для задачи с ID {task_id}")
        await c.answer("Произошла ошибка при сохранении категорий. Попробуйте еще раз.")

async def on_create_task(message: Message, message_input: MessageInput, manager: DialogManager) -> None:
    """
    Обработчик создания задачи.

    Args:
        message (Message): Объект сообщения.
        message_input (MessageInput): Виджет ввода сообщения.
        manager (DialogManager): Менеджер диалога.

    Returns:
        None
    """
    try:
        user_token: str = manager.dialog_data.get("user_token")
        title: str = message.text
        locale: str = manager.dialog_data.get("locale", "ru")

        logger.info(f"Начало создания новой задачи с заголовком: {title}")

        manager.dialog_data["task_title"] = title
        await manager.switch_to(MainSG.create_task_description)
    except Exception as e:
        logger.log_exception("Ошибка при создании задачи")
        await message.answer("Произошла ошибка при создании задачи. Попробуйте еще раз.")

async def on_task_description(message: Message, message_input: MessageInput, manager: DialogManager) -> None:
    """
    Обработчик ввода описания задачи.

    Args:
        message (Message): Объект сообщения.
        message_input (MessageInput): Виджет ввода сообщения.
        manager (DialogManager): Менеджер диалога.

    Returns:
        None
    """
    try:
        description: str = message.text
        manager.dialog_data["task_description"] = description
        locale: str = manager.dialog_data.get("locale", "ru")

        logger.info("Добавлено описание задачи")

        await manager.switch_to(MainSG.create_task_due_date)
    except Exception as e:
        logger.log_exception("Ошибка при добавлении описания задачи")
        await message.answer("Произошла ошибка при добавлении описания задачи. Попробуйте еще раз.")

async def on_task_due_date(message: Message, message_input: MessageInput, manager: DialogManager) -> None:
    """
    Обработчик ввода срока выполнения задачи.

    Args:
        message (Message): Объект сообщения.
        message_input (MessageInput): Виджет ввода сообщения.
        manager (DialogManager): Менеджер диалога.

    Returns:
        None
    """
    try:
        due_date: str = message.text
        manager.dialog_data["task_due_date"] = due_date
        locale: str = manager.dialog_data.get("locale", "ru")
        logger.info("Добавлен срок выполнения задачи")

        await manager.switch_to(MainSG.create_task_categories)
    except Exception as e:
        logger.log_exception("Ошибка при добавлении срока выполнения задачи")
        await message.answer("Произошла ошибка при добавлении срока выполнения задачи. Попробуйте еще раз.")

async def on_update_title(message: Message, message_input: MessageInput, manager: DialogManager) -> None:
    """
    Обработчик обновления заголовка задачи.

    Args:
        message (Message): Объект сообщения.
        message_input (MessageInput): Виджет ввода сообщения.
        manager (DialogManager): Менеджер диалога.

    Returns:
        None
    """
    try:
        user_token: str = manager.dialog_data.get("user_token")
        task_id: str = manager.dialog_data.get("selected_task_id")
        new_title: str = message.text
        logger.info(f"Попытка обновления заголовка задачи с ID: {task_id}")
        success: bool = await api_service.update_task(user_token, task_id, title=new_title)
        if success:
            logger.info(f"Заголовок задачи с ID {task_id} успешно обновлен")
            await manager.switch_to(MainSG.update_task_description)
        else:
            logger.warning(f"Не удалось обновить заголовок задачи с ID {task_id}")
            await message.answer(localization.get_text("error_updating_task", manager.dialog_data.get("locale", "ru")))
    except Exception as e:
        logger.log_exception(f"Ошибка при обновлении заголовка задачи с ID {task_id}")
        await message.answer("Произошла ошибка при обновлении заголовка задачи. Попробуйте еще раз.")

async def on_update_description(message: Message, message_input: MessageInput, manager: DialogManager) -> None:
    """
    Обработчик обновления описания задачи.

    Args:
        message (Message): Объект сообщения.
        message_input (MessageInput): Виджет ввода сообщения.
        manager (DialogManager): Менеджер диалога.

    Returns:
        None
    """
    try:
        user_token: str = manager.dialog_data.get("user_token")
        task_id: str = manager.dialog_data.get("selected_task_id")
        new_description: str = message.text
        logger.info(f"Попытка обновления описания задачи с ID: {task_id}")
        success: bool = await api_service.update_task(user_token, task_id, description=new_description)
        if success:
            logger.info(f"Описание задачи с ID {task_id} успешно обновлено")
            await manager.switch_to(MainSG.update_task_due_date)
        else:
            logger.warning(f"Не удалось обновить описание задачи с ID {task_id}")
            await message.answer(localization.get_text("error_updating_task", manager.dialog_data.get("locale", "ru")))
    except Exception as e:
        logger.log_exception(f"Ошибка при обновлении описания задачи с ID {task_id}")
        await message.answer("Произошла ошибка при обновлении описания задачи. Попробуйте еще раз.")

async def on_update_due_date(message: Message, message_input: MessageInput, manager: DialogManager) -> None:
    """
    Обработчик обновления срока выполнения задачи.

    Args:
        message (Message): Объект сообщения.
        message_input (MessageInput): Виджет ввода сообщения.
        manager (DialogManager): Менеджер диалога.

    Returns:
        None
    """
    try:
        user_token: str = manager.dialog_data.get("user_token")
        task_id: str = manager.dialog_data.get("selected_task_id")
        new_due_date: str = message.text
        logger.info(f"Попытка обновления срока выполнения задачи с ID: {task_id}")
        success: bool = await api_service.update_task(user_token, task_id, due_date=new_due_date)
        if success:
            logger.info(f"Срок выполнения задачи с ID {task_id} успешно обновлен")
            await message.answer(
                localization.get_text("succes_updating_task", manager.dialog_data.get("locale", "ru")))
            await manager.switch_to(MainSG.task_details)
        else:
            logger.warning(f"Не удалось обновить срок выполнения задачи с ID {task_id}")
            await message.answer(localization.get_text("error_updating_task", manager.dialog_data.get("locale", "ru")))
    except Exception as e:
        logger.log_exception(f"Ошибка при обновлении срока выполнения задачи с ID {task_id}")
        await message.answer("Произошла ошибка при обновлении срока выполнения задачи. Попробуйте еще раз.")

async def on_task_categories(message: Message, message_input: MessageInput, manager: DialogManager) -> None:
    """
    Обработчик ввода категорий задачи.

    Args:
        message (Message): Объект сообщения.
        message_input (MessageInput): Виджет ввода сообщения.
        manager (DialogManager): Менеджер диалога.

    Returns:
        None
    """
    try:
        categories: List[str] = [cat.strip() for cat in message.text.split(',')]
        user_token: str = manager.dialog_data.get("user_token")
        title: str = manager.dialog_data.get("task_title")
        description: str = manager.dialog_data.get("task_description")
        due_date: str = manager.dialog_data.get("task_due_date")
        locale: str = manager.dialog_data.get("locale", "ru")

        logger.info(f"Попытка создания задачи с категориями: {categories}")
        task: Optional[Dict[str, Any]] = await api_service.create_task(user_token, title, description, due_date, categories)

        if task:
            logger.info(f"Задача успешно создана с ID: {task.get('id')}")
            await manager.event.answer(localization.get_text("task_created", locale))
            await manager.switch_to(MainSG.tasks)
        else:
            logger.warning("Не удалось создать задачу")
            await manager.event.answer(localization.get_text("error_creating_task", locale))
    except Exception as e:
        logger.log_exception("Ошибка при создании задачи с категориями")
        await message.event.answer("Произошла ошибка при создании задачи. Попробуйте еще раз.")

async def on_create_category(message: Message, message_input: MessageInput, manager: DialogManager) -> None:
    """
    Обработчик создания новой категории.

    Args:
        message (Message): Объект сообщения.
        message_input (MessageInput): Виджет ввода сообщения.
        manager (DialogManager): Менеджер диалога.

    Returns:
        None
    """
    try:
        user_token: str = manager.dialog_data.get("user_token")
        name: str = message.text
        category: Optional[Dict[str, Any]] = await api_service.create_category(user_token, name)
        locale: str = manager.dialog_data.get("locale", "ru")

        if category:
            logger.info(f"Категория успешно создана с ID: {category.get('id')}")
            await manager.event.answer(localization.get_text("category_created", locale))
            await manager.switch_to(MainSG.categories)
        else:
            logger.warning(f"Не удалось создать категорию с именем: {name}")
            await manager.event.answer(localization.get_text("error_creating_category", locale))
    except Exception as e:
        logger.log_exception("Ошибка при создании категории")
        await message.answer("Произошла ошибка при создании категории. Попробуйте еще раз.")

async def on_create_comment(message: Message, message_input: MessageInput, manager: DialogManager) -> None:
    """
    Обработчик создания нового комментария.

    Args:
        message (Message): Объект сообщения.
        message_input (MessageInput): Виджет ввода сообщения.
        manager (DialogManager): Менеджер диалога.

    Returns:
        None
    """
    try:
        user_token: str = manager.dialog_data.get("user_token")
        content: str = message.text
        task_id: str = manager.dialog_data.get("selected_task_id")
        user_id: int = message.from_user.id
        comment: Optional[Dict[str, Any]] = await api_service.create_comment(user_token, task_id, user_id, content)
        locale: str = manager.dialog_data.get("locale", "ru")

        if comment:
            logger.info(f"Комментарий успешно создан с ID: {comment.get('id')}")
            await manager.event.answer(localization.get_text("comment_created", locale))
            await manager.switch_to(MainSG.comments)
        else:
            logger.warning(f"Не удалось создать комментарий для задачи с ID: {task_id}")
            await manager.event.answer(localization.get_text("error_creating_comment", locale))
    except Exception as e:
        logger.log_exception(f"Ошибка при создании комментария для задачи с ID {task_id}")
        await message.event.answer("Произошла ошибка при создании комментария. Попробуйте еще раз.")

async def on_complete_and_delete_task(c: CallbackQuery, widget: Button, manager: DialogManager) -> None:
    """
    Обработчик завершения и удаления задачи.

    Args:
        c (CallbackQuery): Объект обратного вызова.
        widget (Button): Виджет кнопки.
        manager (DialogManager): Менеджер диалога.

    Returns:
        None
    """
    try:
        user_token: str = manager.dialog_data.get("user_token")
        task_id: str = manager.dialog_data.get("selected_task_id")
        locale: str = manager.dialog_data.get("locale", "ru")
        logger.info(f"Попытка завершения и удаления задачи с ID: {task_id}")

        success: bool = await api_service.complete_and_delete_task(user_token, task_id)

        if success:
            logger.info(f"Задача с ID {task_id} успешно завершена и удалена")
            await c.answer(localization.get_text("task_completed_and_deleted", locale), show_alert=True)
            await manager.switch_to(MainSG.tasks)
        else:
            logger.warning(f"Не удалось завершить и удалить задачу с ID {task_id}")
            await c.answer(localization.get_text("error_completing_and_deleting_task", locale), show_alert=True)
    except Exception as e:
        logger.log_exception(f"Ошибка при завершении и удалении задачи с ID {task_id}")
        await c.answer("Произошла ошибка при завершении и удалении задачи. Попробуйте еще раз.")
