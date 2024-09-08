from aiogram import Dispatcher, types
from aiogram.filters import Command
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.kbd import Button, Row, Column, ScrollingGroup, Select
from aiogram_dialog.widgets.text import Const, Format
from aiogram.fsm.state import State, StatesGroup
from utils.i18n import _, i18n_middleware, i18n
from utils.database import set_user_locale, get_or_create_user, get_user_locale
from utils.token_storage import save_user_token, get_user_token
from services import django_api, fastapi_api
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from typing import Any


class StartSG(StatesGroup):
    choose_language = State()
    main_menu = State()
    view_tasks = State()
    task_details = State()
    create_task = State()
    auth_error = State()
    add_comment = State()
    update_task = State()


async def start_handler(message: types.Message, dialog_manager: DialogManager):
    user_id = message.from_user.id
    locale = await get_user_locale(user_id)

    if locale:
        dialog_manager.middleware_data["i18n"].current_locale = locale
        i18n.current_locale = locale
        await dialog_manager.start(StartSG.main_menu, mode=StartMode.RESET_STACK)
    else:
        await dialog_manager.start(StartSG.choose_language, mode=StartMode.RESET_STACK)


async def on_language_selected(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    lang = button.widget_id
    user_id = callback.from_user.id
    await set_user_locale(user_id, lang)
    dialog_manager.middleware_data["i18n"].current_locale = lang
    i18n.current_locale = lang
    await callback.answer(_("language_changed"))
    await dialog_manager.switch_to(StartSG.main_menu)


async def get_user_info(dialog_manager: DialogManager, **kwargs):
    user_id = dialog_manager.event.from_user.id
    username = dialog_manager.event.from_user.username or str(user_id)

    db_id, locale = await get_or_create_user(user_id)
    dialog_manager.middleware_data["i18n"].current_locale = locale
    i18n.current_locale = locale

    password = f"todo_Telegram_{user_id}"

    user_exists = await django_api.check_user(user_id)
    if not user_exists:
        await django_api.create_user(user_id, username, password)

    token = await django_api.get_token(username, password)
    if token:
        await save_user_token(dialog_manager.middleware_data["state"], token)
        return {
            "start_message": _("start_message"),
            "main_menu_translated": _("main_menu"),
            "view_tasks": _("view_tasks"),
            "create_task": _("create_task"),
            "change_language": _("change_language"),
        }
    else:
        await dialog_manager.switch_to(StartSG.auth_error)
        return {"auth_message": _("authorization_error")}


async def get_tasks_list(dialog_manager: DialogManager, **kwargs):
    user_id = dialog_manager.event.from_user.id
    db_id, locale = await get_or_create_user(user_id)
    dialog_manager.middleware_data["i18n"].current_locale = locale
    i18n.current_locale = locale

    token = await get_user_token(dialog_manager.middleware_data["state"])
    tasks = await django_api.get_tasks(token)

    formatted_tasks = [
        {
            "id": task["id"],
            "title": f"{'✅' if task['completed'] else '❌'} {task['title']}"
        }
        for task in tasks
    ]

    return {
        "tasks": formatted_tasks,
        "task_list": _("task_list"),
        "back": _("back"),
    }


async def on_task_selected(callback: CallbackQuery, widget: Any, dialog_manager: DialogManager, item_id: str):
    await dialog_manager.start(StartSG.task_details, data={"task_id": str(item_id)})


async def get_task_details(dialog_manager: DialogManager, **kwargs):
    token = await get_user_token(dialog_manager.middleware_data["state"])
    task_id = dialog_manager.start_data["task_id"]
    task = await django_api.get_task_details(token, task_id)
    comments = await fastapi_api.get_comments(token, task_id)

    task_title = task.get('title', _('No title'))
    task_description = task.get('description', _('No description'))
    task_due_date = task.get('due_date', _('No due date'))
    task_completed = task.get('completed', False)

    formatted_comments = []
    for comment in comments:
        username = comment.get('username', _('Unknown user'))
        content = comment.get('content', _('No content'))
        formatted_comments.append(f"{username}: {content}")

    return {
        "task_details": _("task_details"),
        "due_date": _("due_date"),
        "status": _("status"),
        "comments_title": _("comment_list"),
        "task_title": _("task_title"),
        "task_description": _("task_description"),
        "task": {
            "id": task.get('id', ''),
            "title": task_title,
            "description": task_description,
            "due_date": task_due_date,
            "completed": task_completed
        },
        "task_status": "✅" if task_completed else "❌",
        "formatted_comments": "\n".join(formatted_comments),
        "back": _("back"),
        "add_comment": _("add_comment"),
        "update_task": _("update_task"),
        "complete_task": _("complete_task"),
        "complete_and_delete_task": _("complete_and_delete_task"),
    }


async def on_create_task(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(StartSG.create_task)


async def process_create_task(message: Message, dialog_manager: DialogManager, state: FSMContext):
    user_data = await state.get_data()
    if "title" not in user_data:
        await state.update_data(title=message.text)
        await message.answer(_("enter_task_description"))
    elif "description" not in user_data:
        await state.update_data(description=message.text)
        await message.answer(_("enter_task_due_date"))
    elif "due_date" not in user_data:
        await state.update_data(due_date=message.text)
        await message.answer(_("enter_task_categories"))
    else:
        user_data = await state.get_data()
        categories = message.text.split(',')
        token = await get_user_token(dialog_manager.middleware_data["state"])
        task = await django_api.create_task(token, user_data["title"], user_data["description"], user_data["due_date"],
                                            categories)
        if task:
            await message.answer(_("task_created_successfully"))
        else:
            await message.answer(_("task_creation_error"))
        await state.clear()
        await dialog_manager.switch_to(StartSG.main_menu)


async def on_add_comment_click(c: CallbackQuery, button: Button, manager: DialogManager):
    await manager.switch_to(StartSG.add_comment)


async def on_update_task_click(c: CallbackQuery, button: Button, manager: DialogManager):
    await manager.switch_to(StartSG.update_task)


async def on_complete_task_click(c: CallbackQuery, button: Button, manager: DialogManager):
    task_id = manager.start_data["task_id"]
    token = await get_user_token(manager.middleware_data["state"])
    updated_task = await django_api.update_task(token, task_id, {"completed": True})
    if updated_task:
        await manager.update({"task": updated_task})
    await c.answer(_("task_completed"))


async def on_complete_and_delete_task_click(c: CallbackQuery, button: Button, manager: DialogManager):
    task_id = manager.start_data["task_id"]
    token = await get_user_token(manager.middleware_data["state"])
    await django_api.update_task(token, task_id, {"completed": True})
    deleted = await django_api.delete_task(token, task_id)
    if deleted:
        await manager.switch_to(StartSG.view_tasks)
        await c.answer(_("task_completed_and_deleted"))
    else:
        await c.answer(_("error_deleting_task"))


async def process_add_comment(message: Message, dialog_manager: DialogManager, state: FSMContext):
    task_id = dialog_manager.start_data["task_id"]
    token = await get_user_token(dialog_manager.middleware_data["state"])
    user_id = message.from_user.id
    comment = await fastapi_api.create_comment(token, task_id, message.text, user_id)
    if comment:
        await message.answer(_("comment_added"))
    else:
        await message.answer(_("error_adding_comment"))
    await dialog_manager.switch_to(StartSG.task_details)


async def process_update_task(message: Message, dialog_manager: DialogManager, state: FSMContext):
    task_id = dialog_manager.start_data["task_id"]
    token = await get_user_token(dialog_manager.middleware_data["state"])
    user_data = await state.get_data()
    if "title" not in user_data:
        await state.update_data(title=message.text)
        await message.answer(_("enter_task_description"))
    elif "description" not in user_data:
        await state.update_data(description=message.text)
        user_data = await state.get_data()
        updated_task = await django_api.update_task(token, task_id,
                                                    {"title": user_data["title"], "description": message.text})
        if updated_task:
            await message.answer(_("task_updated"))
        else:
            await message.answer(_("error_updating_task"))
        await state.clear()
        await dialog_manager.switch_to(StartSG.task_details)


start_dialog = Dialog(
    Window(
        Const(_("choose_language")),
        Row(
            Button(Const("Русский 🇷🇺"), id="ru", on_click=on_language_selected),
            Button(Const("English 🇬🇧"), id="en", on_click=on_language_selected),
        ),
        state=StartSG.choose_language,
    ),
    Window(
        Format("{start_message}\n\n{main_menu_translated}\n"),
        Column(
            Button(Format("{view_tasks}"), id="view_tasks", on_click=lambda c, b, m: m.switch_to(StartSG.view_tasks)),
            Button(Format("{create_task}"), id="create_task", on_click=on_create_task),
            Button(Format("{change_language}"), id="change_language",
                   on_click=lambda c, b, m: m.switch_to(StartSG.choose_language)),
        ),
        state=StartSG.main_menu,
        getter=get_user_info,
    ),
    Window(
        Format("{task_list}"),
        ScrollingGroup(
            Select(
                Format("{item[title]}"),
                id="tasks",
                item_id_getter=lambda x: str(x["id"]),
                items="tasks",
                on_click=on_task_selected,
            ),
            id="tasks_group",
            width=1,
            height=10,
        ),
        Button(Format("{back}"), id="back", on_click=lambda c, b, m: m.switch_to(StartSG.main_menu)),
        state=StartSG.view_tasks,
        getter=get_tasks_list,
    ),
    Window(
        Format(
            "{task_details}\n"
            "ID: {task[id]}\n"
            "{task_title}: {task[title]}\n"
            "{task_description}: {task[description]}\n"
            "{due_date}: {task[due_date]}\n"
            "{status}: {task_status}\n\n"
            "{comments_title}:\n"
            "{formatted_comments}"
        ),
        Row(
            Button(Format("{add_comment}"), id="add_comment", on_click=on_add_comment_click),
            Button(Format("{update_task}"), id="update_task", on_click=on_update_task_click),
        ),
        Row(
            Button(Format("{complete_task}"), id="complete_task", on_click=on_complete_task_click),
            Button(Format("{complete_and_delete_task}"), id="complete_and_delete_task",
                   on_click=on_complete_and_delete_task_click),
        ),
        Button(Format("{back}"), id="back", on_click=lambda c, b, m: m.switch_to(StartSG.view_tasks)),
        state=StartSG.task_details,
        getter=get_task_details,
    ),
    Window(
        Const(_("enter_task_title")),
        state=StartSG.create_task,
    ),
    Window(
        Format("{auth_message}"),
        state=StartSG.auth_error,
        getter=get_user_info,
    ),
    Window(
        Const(_("enter_comment")),
        Button(Const(_("back")), id="back", on_click=lambda c, b, m: m.switch_to(StartSG.task_details)),
        state=StartSG.add_comment,
    ),
    Window(
        Const(_("enter_new_task_title")),
        Button(Const(_("back")), id="back", on_click=lambda c, b, m: m.switch_to(StartSG.task_details)),
        state=StartSG.update_task,
    ),
)


def register_start_handlers(dp: Dispatcher):
    dp.message.register(start_handler, Command("start"))
    dp.message.register(process_create_task, StartSG.create_task)
    dp.message.register(process_add_comment, StartSG.add_comment)
    dp.message.register(process_update_task, StartSG.update_task)
    dp.include_router(start_dialog)