from aiogram.filters.state import StatesGroup, State
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import ScrollingGroup, Button, Row, Select, Back, Next, Group
from aiogram_dialog.widgets.text import Const, Format, Jinja
from aiogram_dialog.widgets.input import MessageInput
from services.api import api_service
from utils.localization import localization
from datetime import datetime


class MainSG(StatesGroup):
    language_select = State()
    main = State()
    tasks = State()
    create_task = State()
    create_task_description = State()
    create_task_due_date = State()
    create_task_categories = State()
    task_details = State()
    categories = State()
    create_category = State()
    comments = State()
    create_comment = State()

async def on_task_selected(c, widget, manager, item_id):
    manager.dialog_data["selected_task_id"] = str(item_id)
    await manager.switch_to(MainSG.task_details)

async def on_language_selected(c, select, manager):
    language = select.item_id
    user = manager.event.from_user
    await localization.set_user_locale(user.id, language)
    await manager.switch_to(MainSG.main)


async def check_user(dialog_manager, **kwargs):
    user = dialog_manager.event.from_user
    telegram_id = user.id
    username = user.username or user.full_name
    password = f"todo_Telegram_{telegram_id}"

    user_info = await api_service.get_user_info(telegram_id)
    if not user_info:
        user_info = await api_service.create_user(telegram_id, username, password)

    if user_info:
        locale = await localization.get_user_locale(telegram_id)
        user_token, user_id = await api_service.user_login(username, password)
        if user_token:
            dialog_manager.dialog_data["user_token"] = user_token
            return {
                "user": user_info,
                "locale": locale,
                "main_menu": localization.get_text("main_menu", locale),
                "my_tasks": localization.get_text("my_tasks", locale),
                "categories": localization.get_text("categories", locale),
                "create_task": localization.get_text("create_task", locale),
                "back": localization.get_text("back", locale),
                "task_details": localization.get_text("task_details", locale),
                "comments": localization.get_text("comments", locale),
                "create_comment": localization.get_text("create_comment", locale),
                "enter_task_name": localization.get_text("enter_task_name", locale),
                "enter_task_description": localization.get_text("enter_task_description", locale),
                "enter_task_due_date": localization.get_text("enter_task_due_date", locale),
                "enter_task_categories": localization.get_text("enter_task_categories", locale),
                "enter_category_name": localization.get_text("enter_category_name", locale),
                "enter_comment_text": localization.get_text("enter_comment_text", locale),
            }
    return {"error": localization.get_text("error_user_creation", locale)}


async def get_tasks(dialog_manager, **kwargs):
    user_token = dialog_manager.dialog_data.get("user_token")
    tasks = await api_service.get_tasks(user_token)
    locale = dialog_manager.dialog_data.get("locale", "ru")
    return {
        "tasks": tasks,
        "create_task": localization.get_text("create_task", locale),
        "no_tasks": localization.get_text("no_tasks", locale),
        "my_tasks": localization.get_text("my_tasks", locale),
        "back": localization.get_text("back", locale),
    }


async def get_task_details(dialog_manager, **kwargs):
    user_token = dialog_manager.dialog_data.get("user_token")
    task_id = dialog_manager.dialog_data.get("selected_task_id")
    locale = dialog_manager.dialog_data.get("locale", "ru")

    task = await api_service.get_task(user_token, task_id)

    if task['due_date']:
        due_date = datetime.fromisoformat(task['due_date'])
        task['due_date'] = due_date.strftime('%d.%m.%Y')

    return {
        "task": task,
        "assign_categories_emoji": localization.get_text("assign_categories_emoji", locale),
        "update_task_emoji": localization.get_text("update_task_emoji", locale),
        "complete_and_delete_task_emoji": localization.get_text("complete_and_delete_task_emoji", locale),
        "task_details": localization.get_text("task_details", locale),
        "task_description": localization.get_text("task_description", locale),
        "task_due_date": localization.get_text("task_due_date", locale),
        "comments": localization.get_text("comments", locale),
        "back": localization.get_text("back", locale),
    }

async def get_categories(dialog_manager, **kwargs):
    user_token = dialog_manager.dialog_data.get("user_token")
    categories = await api_service.get_categories(user_token)
    locale = dialog_manager.dialog_data.get("locale", "ru")
    for category in categories:
        category["delete_category"] = localization.get_text("delete_category", locale)

    formatted_categories = "\n\n".join([
        f"Категория: {category['name']}\n"
        for category in categories
    ])

    return {
        "categories": categories,
        "categories_format": formatted_categories,
        "no_categories": localization.get_text("no_categories", locale),
        "categories_title": localization.get_text("categories", locale),
        "create_category": localization.get_text("create_category", locale),
        "back": localization.get_text("back", locale),
    }


async def get_comments(dialog_manager, **kwargs):
    user_token = dialog_manager.dialog_data.get("user_token")
    task_id = dialog_manager.dialog_data.get("selected_task_id")
    comments = await api_service.get_comments(user_token, task_id)
    locale = dialog_manager.dialog_data.get("locale", "ru")
    for comment in comments:
        comment["delete_comment"] = localization.get_text("delete_comment", locale)

    formatted_comments = "\n\n".join([
        f"ID: {comment['id']}\n"
        f"Содержание: {comment['content']}"
        for comment in comments
    ])

    return {
        "comments": formatted_comments,
        "comments_list": comments,
        "no_comments": localization.get_text("no_comments", locale),
        "comments_title": localization.get_text("comments", locale),
        "create_comment": localization.get_text("create_comment", locale),
        "back": localization.get_text("back", locale),
    }

async def get_create_comment(dialog_manager: DialogManager, **kwargs):
    locale = dialog_manager.dialog_data.get("locale", "ru")
    return {
        "create_comment": localization.get_text("create_comment", locale),
        "enter_comment_text": localization.get_text("enter_comment_text", locale),
        "back": localization.get_text("back", locale),
    }

async def get_create_category(dialog_manager: DialogManager, **kwargs):
    locale = dialog_manager.dialog_data.get("locale", "ru")
    return {
        "create_category": localization.get_text("create_category", locale),
        "enter_category_name": localization.get_text("enter_category_name", locale),
        "back": localization.get_text("back", locale),
    }

async def on_delete_comment(c, widget: Button, manager: DialogManager, item_id: str):
    user_token = manager.dialog_data.get("user_token")
    success = await api_service.delete_comment(user_token, item_id)
    locale = manager.dialog_data.get("locale", "ru")

    if success:
        text = localization.get_text("comment_deleted", locale)
    else:
        text = localization.get_text("error_deleting_comment", locale)

    # Обновляем список комментариев
    task_id = manager.dialog_data.get("selected_task_id")
    comments = await api_service.get_comments(user_token, task_id)

    # Обновляем данные диалога
    await manager.update({
        "comments_list": comments,
        "comments": "\n\n".join([
            f"ID: {comment['id']}\nСодержание: {comment['content']}"
            for comment in comments
        ])
    })

    # Отправляем уведомление
    await c.answer(text)

    # Перерисовываем текущее окно
    return await manager.switch_to(MainSG.comments)

async def on_category_selected(c, widget: Button, manager: DialogManager, item_id: str):
    user_token = manager.dialog_data.get("user_token")
    success = await api_service.delete_category(user_token, item_id)
    locale = manager.dialog_data.get("locale", "ru")

    if success:
        text = localization.get_text("category_deleted", locale)
    else:
        text = localization.get_text("error_deleting_category", locale)

    await c.answer(text, show_alert=True)
    await manager.update({"categories": await api_service.get_categories(user_token)})


async def on_create_task(message, message_input, manager):
    user_token = manager.dialog_data.get("user_token")
    title = message.text
    locale = manager.dialog_data.get("locale", "ru")

    manager.dialog_data["task_title"] = title
    await manager.answer(localization.get_text("enter_task_description", locale))
    await manager.switch_to(MainSG.create_task_description)


async def on_task_description(message, message_input, manager):
    description = message.text
    manager.dialog_data["task_description"] = description
    locale = manager.dialog_data.get("locale", "ru")

    await manager.answer(localization.get_text("enter_task_due_date", locale))
    await manager.switch_to(MainSG.create_task_due_date)


async def on_task_due_date(message, message_input, manager):
    due_date = message.text
    manager.dialog_data["task_due_date"] = due_date
    locale = manager.dialog_data.get("locale", "ru")

    await manager.answer(localization.get_text("enter_task_categories", locale))
    await manager.switch_to(MainSG.create_task_categories)


async def on_task_categories(message, message_input, manager):
    categories = [cat.strip() for cat in message.text.split(',')]
    user_token = manager.dialog_data.get("user_token")
    title = manager.dialog_data.get("task_title")
    description = manager.dialog_data.get("task_description")
    due_date = manager.dialog_data.get("task_due_date")
    locale = manager.dialog_data.get("locale", "ru")

    task = await api_service.create_task(user_token, title, description, due_date, categories)

    if task:
        await manager.answer(localization.get_text("task_created", locale))
        await manager.switch_to(MainSG.tasks)
    else:
        await manager.answer(localization.get_text("error_creating_task", locale))


async def on_create_category(message, message_input, manager):
    user_token = manager.dialog_data.get("user_token")
    name = message.text
    category = await api_service.create_category(user_token, name)
    locale = manager.dialog_data.get("locale", "ru")

    if category:
        await manager.answer(localization.get_text("category_created", locale))
        await manager.switch_to(MainSG.categories)
    else:
        await manager.answer(localization.get_text("error_creating_category", locale))


async def on_create_comment(message, message_input, manager):
    user_token = manager.dialog_data.get("user_token")
    content = message.text
    task_id = manager.dialog_data.get("selected_task_id")
    user_id = message.from_user.id
    comment = await api_service.create_comment(user_token, task_id, user_id, content)
    locale = manager.dialog_data.get("locale", "ru")

    if comment:
        await manager.event.answer(localization.get_text("comment_created", locale))
        await manager.switch_to(MainSG.comments)
    else:
        await manager.answer(localization.get_text("error_creating_comment", locale))


main_dialog = Dialog(
    Window(
        Const("Select your language / Выберите язык"),
        Select(
            Format("{item[0]}"),
            id="language_select",
            item_id_getter=lambda x: x[1],
            items=[("English 🇬🇧", "en"), ("Русский 🇷🇺", "ru")],
            on_click=on_language_selected
        ),
        state=MainSG.language_select
    ),
    Window(
        Format("{main_menu}"),
        Button(Format("{my_tasks}"), id="tasks", on_click=lambda c, b, m: m.switch_to(MainSG.tasks)),
        Button(Format("{categories}"), id="categories", on_click=lambda c, b, m: m.switch_to(MainSG.categories)),
        state=MainSG.main,
        getter=check_user
    ),
    Window(
        Format("{my_tasks}"),
        Group(
            Select(
                Format("{item[title]}"),
                id="tasks_select",
                item_id_getter=lambda x: x["id"],
                items="tasks",
                on_click=on_task_selected
            ),
            width=1,
        ),
        Button(Format("{create_task}"), id="create_task", on_click=lambda c, b, m: m.switch_to(MainSG.create_task)),
        Button(Format("{back}"), id="back", on_click=lambda c, b, m: m.switch_to(MainSG.main)),
        getter=get_tasks,
        state=MainSG.tasks
    ),
    Window(
        Format("{create_task}"),
        Format("{enter_task_name}"),
        MessageInput(on_create_task),
        Back(Format("{back}")),
        state=MainSG.create_task
    ),
    Window(
        Format("{enter_task_description}"),
        MessageInput(on_task_description),
        Back(Format("{back}")),
        state=MainSG.create_task_description
    ),
    Window(
        Format("{enter_task_due_date}"),
        MessageInput(on_task_due_date),
        Back(Format("{back}")),
        state=MainSG.create_task_due_date
    ),
    Window(
        Format("{enter_task_categories}"),
        MessageInput(on_task_categories),
        Back(Format("{back}")),
        state=MainSG.create_task_categories
    ),
    Window(
        Format("{task_details}: {task[title]}"),
        Format("{task_description}: {task[description]}"),
        Format("{task_due_date}: {task[due_date]}"),
        Button(Format("{comments}"), id="comments", on_click=lambda c, b, m: m.switch_to(MainSG.comments)),
        Button(Format("{assign_categories_emoji}"), id="assign_categories_emoji", on_click=lambda c, b, m: m.switch_to(MainSG.comments)),
        Button(Format("{update_task_emoji}"), id="update_task_emoji", on_click=lambda c, b, m: m.switch_to(MainSG.comments)),
        Button(Format("{complete_and_delete_task_emoji}"), id="complete_and_delete_task_emoji", on_click=lambda c, b, m: m.switch_to(MainSG.comments)),
        Button(Format("{back}"), id="back", on_click=lambda c, b, m: m.switch_to(MainSG.tasks)),
        getter=get_task_details,
        state=MainSG.task_details
    ),
    Window(
        Format("{categories_title}"),
        Format("{categories_format}"),
        Group(
            Select(
                Format("{item[delete_category]} \"{item[name]}\""),
                id="categories_select",
                item_id_getter=lambda x: x["id"],
                items="categories",
                on_click=on_category_selected
            ),
            width=1
        ),
        Button(Format("{create_category}"), id="create_category",
               on_click=lambda c, b, m: m.switch_to(MainSG.create_category)),
        Button(Format("{back}"), id="back", on_click=lambda c, b, m: m.switch_to(MainSG.main)),
        getter=get_categories,
        state=MainSG.categories
    ),
    Window(
        Format("{create_category}"),
        Format("{enter_category_name}"),
        MessageInput(on_create_category),
        Back(Format("{back}")),
        state=MainSG.create_category,
        getter=get_create_category
    ),
    Window(
        Format("{comments_title}"),
        Format("{comments}"),
        Group(
            Select(
                Jinja("{{ item.delete_comment }} \"{{ item.content }}\""),
                id="comments_select",
                item_id_getter=lambda x: x["id"],
                items="comments_list",
                on_click=on_delete_comment
            ),
            width=1
        ),
        Button(Format("{create_comment}"), id="create_comment",
               on_click=lambda c, b, m: m.switch_to(MainSG.create_comment)),
        Button(Format("{back}"), id="back", on_click=lambda c, b, m: m.switch_to(MainSG.task_details)),
        getter=get_comments,
        state=MainSG.comments
    ),
    Window(
        Format("{create_comment}"),
        Format("{enter_comment_text}"),
        MessageInput(on_create_comment),
        Back(Format("{back}")),
        getter=get_create_comment,
        state=MainSG.create_comment
    )
)