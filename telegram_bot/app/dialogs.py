from aiogram.filters.state import StatesGroup, State
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import ScrollingGroup, Button, Row, Select, Back, Next, Group
from aiogram_dialog.widgets.text import Const, Format, Jinja
from aiogram_dialog.widgets.input import MessageInput
from services.api import api_service
from utils.localization import localization
from datetime import datetime
from typing import List, Dict, Any, Optional
from aiogram.types import CallbackQuery, Message

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
    assign_categories = State()
    update_task = State()
    complete_and_delete_task = State()
    update_task_title = State()
    update_task_description = State()
    update_task_due_date = State()

async def on_task_selected(c: CallbackQuery, widget: Any, manager: DialogManager, item_id: str) -> None:
    manager.dialog_data["selected_task_id"] = str(item_id)
    await manager.switch_to(MainSG.task_details)

async def on_language_selected(c: CallbackQuery, select: Any, manager: DialogManager) -> None:
    language: str = select.item_id
    user = manager.event.from_user
    await localization.set_user_locale(user.id, language)
    await manager.switch_to(MainSG.main)

async def check_user(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    user = dialog_manager.event.from_user
    telegram_id: int = user.id
    username: str = user.username or user.full_name
    password: str = f"todo_Telegram_{telegram_id}"

    user_info: Optional[Dict[str, Any]] = await api_service.get_user_info(telegram_id)
    if not user_info:
        user_info = await api_service.create_user(telegram_id, username, password)

    if user_info:
        locale: str = await localization.get_user_locale(telegram_id)
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

async def get_tasks(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    user_token: str = dialog_manager.dialog_data.get("user_token")
    tasks: List[Dict[str, Any]] = await api_service.get_tasks(user_token)
    locale: str = dialog_manager.dialog_data.get("locale", "ru")
    return {
        "tasks": tasks,
        "create_task": localization.get_text("create_task", locale),
        "no_tasks": localization.get_text("no_tasks", locale),
        "my_tasks": localization.get_text("my_tasks", locale),
        "back": localization.get_text("back", locale),
    }

async def get_task_details(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    user_token: str = dialog_manager.dialog_data.get("user_token")
    task_id: str = dialog_manager.dialog_data.get("selected_task_id")
    locale: str = dialog_manager.dialog_data.get("locale", "ru")

    task: Dict[str, Any] = await api_service.get_task(user_token, task_id)

    if task['due_date']:
        due_date: datetime = datetime.fromisoformat(task['due_date'])
        task['due_date'] = due_date.strftime('%d.%m.%Y')

    categories: List[Dict[str, str]] = task.get('categories', [])
    categories_names: str = ", ".join([category['name'] for category in categories])

    return {
        "task": task,
        "categories": categories_names,
        "assign_categories_title": localization.get_text("assign_categories_title", locale),
        "update_task_emoji": localization.get_text("update_task_emoji", locale),
        "complete_and_delete_task_emoji": localization.get_text("complete_and_delete_task_emoji", locale),
        "task_details": localization.get_text("task_details", locale),
        "task_description": localization.get_text("task_description", locale),
        "task_due_date": localization.get_text("task_due_date", locale),
        "task_categories": localization.get_text("categories", locale),
        "comments": localization.get_text("comments", locale),
        "back": localization.get_text("back", locale),
    }

async def get_categories(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    user_token: str = dialog_manager.dialog_data.get("user_token")
    categories: List[Dict[str, Any]] = await api_service.get_categories(user_token)
    locale: str = dialog_manager.dialog_data.get("locale", "ru")
    for category in categories:
        category["delete_category"] = localization.get_text("delete_category", locale)

    formatted_categories: str = "\n\n".join([
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

async def get_categories_for_assignment(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    user_token: str = dialog_manager.dialog_data.get("user_token")
    categories: List[Dict[str, Any]] = await api_service.get_categories(user_token)
    locale: str = dialog_manager.dialog_data.get("locale", "ru")

    dialog_manager.dialog_data["all_categories"] = categories

    return {
        "categories": categories,
        "assign_categories_title": localization.get_text("assign_categories_title", locale),
        "save": localization.get_text("save", locale),
        "back": localization.get_text("back", locale),
    }

async def get_comments(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    user_token: str = dialog_manager.dialog_data.get("user_token")
    task_id: str = dialog_manager.dialog_data.get("selected_task_id")
    comments: List[Dict[str, Any]] = await api_service.get_comments(user_token, task_id)
    locale: str = dialog_manager.dialog_data.get("locale", "ru")
    for comment in comments:
        comment["delete_comment"] = localization.get_text("delete_comment", locale)

    formatted_comments: str = "\n\n".join([
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

async def get_create_comment(dialog_manager: DialogManager, **kwargs) -> Dict[str, str]:
    locale: str = dialog_manager.dialog_data.get("locale", "ru")
    return {
        "create_comment": localization.get_text("create_comment", locale),
        "enter_comment_text": localization.get_text("enter_comment_text", locale),
        "back": localization.get_text("back", locale),
    }

async def get_create_category(dialog_manager: DialogManager, **kwargs) -> Dict[str, str]:
    locale: str = dialog_manager.dialog_data.get("locale", "ru")
    return {
        "create_category": localization.get_text("create_category", locale),
        "enter_category_name": localization.get_text("enter_category_name", locale),
        "back": localization.get_text("back", locale),
    }

async def get_create_task(dialog_manager: DialogManager, **kwargs) -> Dict[str, str]:
    locale: str = dialog_manager.dialog_data.get("locale", "ru")
    return {
        "create_task": localization.get_text("create_task", locale),
        "enter_task_name": localization.get_text("enter_task_name", locale),
        "back": localization.get_text("back", locale),
    }

async def get_task_description(dialog_manager: DialogManager, **kwargs) -> Dict[str, str]:
    locale: str = dialog_manager.dialog_data.get("locale", "ru")
    return {
        "enter_task_description": localization.get_text("enter_task_description", locale),
        "back": localization.get_text("back", locale),
    }

async def get_task_due_date(dialog_manager: DialogManager, **kwargs) -> Dict[str, str]:
    locale: str = dialog_manager.dialog_data.get("locale", "ru")
    return {
        "enter_task_due_date": localization.get_text("enter_task_due_date", locale),
        "back": localization.get_text("back", locale),
    }

async def get_task_categories(dialog_manager: DialogManager, **kwargs) -> Dict[str, str]:
    locale: str = dialog_manager.dialog_data.get("locale", "ru")
    return {
        "enter_task_categories": localization.get_text("enter_task_categories", locale),
        "back": localization.get_text("back", locale),
    }

async def get_update_title(dialog_manager: DialogManager, **kwargs) -> Dict[str, str]:
    locale: str = dialog_manager.dialog_data.get("locale", "ru")
    return {
        "enter_new_title": localization.get_text("enter_new_title", locale),
        "back": localization.get_text("back", locale),
    }

async def get_update_description(dialog_manager: DialogManager, **kwargs) -> Dict[str, str]:
    locale: str = dialog_manager.dialog_data.get("locale", "ru")
    return {
        "enter_new_description": localization.get_text("enter_new_description", locale),
        "back": localization.get_text("back", locale),
    }

async def get_update_due_date(dialog_manager: DialogManager, **kwargs) -> Dict[str, str]:
    locale: str = dialog_manager.dialog_data.get("locale", "ru")
    return {
        "enter_new_due_date": localization.get_text("enter_new_due_date", locale),
        "back": localization.get_text("back", locale),
    }

async def on_delete_comment(c: CallbackQuery, widget: Button, manager: DialogManager, item_id: str) -> None:
    user_token: str = manager.dialog_data.get("user_token")
    success: bool = await api_service.delete_comment(user_token, item_id)
    locale: str = manager.dialog_data.get("locale", "ru")

    if success:
        text: str = localization.get_text("comment_deleted", locale)
    else:
        text: str = localization.get_text("error_deleting_comment", locale)

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

async def on_category_del(c: CallbackQuery, widget: Button, manager: DialogManager, item_id: str) -> None:
    user_token: str = manager.dialog_data.get("user_token")
    success: bool = await api_service.delete_category(user_token, item_id)
    locale: str = manager.dialog_data.get("locale", "ru")

    if success:
        text: str = localization.get_text("category_deleted", locale)
    else:
        text: str = localization.get_text("error_deleting_category", locale)

    await c.answer(text, show_alert=True)
    await manager.update({"categories": await api_service.get_categories(user_token)})

async def on_category_selected(c: CallbackQuery, widget: Button, manager: DialogManager, item_id: str) -> None:
    selected_categories: List[Dict[str, str]] = manager.dialog_data.get("selected_categories", [])
    all_categories: List[Dict[str, Any]] = manager.dialog_data.get("all_categories", [])

    category: Optional[Dict[str, Any]] = next((cat for cat in all_categories if cat['id'] == item_id), None)

    if category:
        existing_category: Optional[Dict[str, str]] = next((cat for cat in selected_categories if cat['id'] == item_id), None)
        if existing_category:
            selected_categories.remove(existing_category)
            await c.answer("❌")
        else:
            selected_categories.append({'name': category['name'], 'id': category['id']})
            await c.answer("✅")
        manager.dialog_data["selected_categories"] = selected_categories

async def on_save_categories(c: CallbackQuery, widget: Button, manager: DialogManager) -> None:
    user_token: str = manager.dialog_data.get("user_token")
    task_id: str = manager.dialog_data.get("selected_task_id")
    locale: str = manager.dialog_data.get("locale", "ru")
    selected_categories: List[Dict[str, str]] = manager.dialog_data.get("selected_categories", [])
    success: bool = await api_service.update_task_categories(user_token, task_id, selected_categories)
    if success:
        await manager.event.answer(localization.get_text("categories_updated", locale))
    else:
        await manager.event.answer(localization.get_text("error_updating_categories", locale))
    await manager.switch_to(MainSG.task_details)

async def on_create_task(message: Message, message_input: MessageInput, manager: DialogManager) -> None:
    user_token: str = manager.dialog_data.get("user_token")
    title: str = message.text
    locale: str = manager.dialog_data.get("locale", "ru")

    manager.dialog_data["task_title"] = title
    await manager.switch_to(MainSG.create_task_description)

async def on_task_description(message: Message, message_input: MessageInput, manager: DialogManager) -> None:
    description: str = message.text
    manager.dialog_data["task_description"] = description
    locale: str = manager.dialog_data.get("locale", "ru")

    await manager.switch_to(MainSG.create_task_due_date)

async def on_task_due_date(message: Message, message_input: MessageInput, manager: DialogManager) -> None:
    due_date: str = message.text
    manager.dialog_data["task_due_date"] = due_date
    locale: str = manager.dialog_data.get("locale", "ru")

    await manager.switch_to(MainSG.create_task_categories)

async def on_update_title(message: Message, message_input: MessageInput, manager: DialogManager) -> None:
    user_token: str = manager.dialog_data.get("user_token")
    task_id: str = manager.dialog_data.get("selected_task_id")
    new_title: str = message.text
    success: bool = await api_service.update_task(user_token, task_id, title=new_title)
    if success:
        await manager.switch_to(MainSG.update_task_description)
    else:
        await message.answer(localization.get_text("error_updating_task", manager.dialog_data.get("locale", "ru")))

async def on_update_description(message: Message, message_input: MessageInput, manager: DialogManager) -> None:
    user_token: str = manager.dialog_data.get("user_token")
    task_id: str = manager.dialog_data.get("selected_task_id")
    new_description: str = message.text
    success: bool = await api_service.update_task(user_token, task_id, description=new_description)
    if success:
        await manager.switch_to(MainSG.update_task_due_date)
    else:
        await message.answer(localization.get_text("error_updating_task", manager.dialog_data.get("locale", "ru")))

async def on_update_due_date(message: Message, message_input: MessageInput, manager: DialogManager) -> None:
    user_token: str = manager.dialog_data.get("user_token")
    task_id: str = manager.dialog_data.get("selected_task_id")
    new_due_date: str = message.text
    success: bool = await api_service.update_task(user_token, task_id, due_date=new_due_date)
    if success:
        await message.answer(
            localization.get_text("succes_updating_task", manager.dialog_data.get("locale", "ru")))
        await manager.switch_to(MainSG.task_details)
    else:
        await message.answer(localization.get_text("error_updating_task", manager.dialog_data.get("locale", "ru")))

async def on_task_categories(message: Message, message_input: MessageInput, manager: DialogManager) -> None:
    categories: List[str] = [cat.strip() for cat in message.text.split(',')]
    user_token: str = manager.dialog_data.get("user_token")
    title: str = manager.dialog_data.get("task_title")
    description: str = manager.dialog_data.get("task_description")
    due_date: str = manager.dialog_data.get("task_due_date")
    locale: str = manager.dialog_data.get("locale", "ru")

    task: Optional[Dict[str, Any]] = await api_service.create_task(user_token, title, description, due_date, categories)

    if task:
        await manager.event.answer(localization.get_text("task_created", locale))
        await manager.switch_to(MainSG.tasks)
    else:
        await manager.event.answer(localization.get_text("error_creating_task", locale))

async def on_create_category(message: Message, message_input: MessageInput, manager: DialogManager) -> None:
    user_token: str = manager.dialog_data.get("user_token")
    name: str = message.text
    category: Optional[Dict[str, Any]] = await api_service.create_category(user_token, name)
    locale: str = manager.dialog_data.get("locale", "ru")

    if category:
        await manager.event.answer(localization.get_text("category_created", locale))
        await manager.switch_to(MainSG.categories)
    else:
        await manager.event.answer(localization.get_text("error_creating_category", locale))

async def on_create_comment(message: Message, message_input: MessageInput, manager: DialogManager) -> None:
    user_token: str = manager.dialog_data.get("user_token")
    content: str = message.text
    task_id: str = manager.dialog_data.get("selected_task_id")
    user_id: int = message.from_user.id
    comment: Optional[Dict[str, Any]] = await api_service.create_comment(user_token, task_id, user_id, content)
    locale: str = manager.dialog_data.get("locale", "ru")

    if comment:
        await manager.event.answer(localization.get_text("comment_created", locale))
        await manager.switch_to(MainSG.comments)
    else:
        await manager.event.answer(localization.get_text("error_creating_comment", locale))

async def on_complete_and_delete_task(c: CallbackQuery, widget: Button, manager: DialogManager) -> None:
    user_token: str = manager.dialog_data.get("user_token")
    task_id: str = manager.dialog_data.get("selected_task_id")
    locale: str = manager.dialog_data.get("locale", "ru")

    success: bool = await api_service.complete_and_delete_task(user_token, task_id)

    if success:
        await c.answer(localization.get_text("task_completed_and_deleted", locale), show_alert=True)
        await manager.switch_to(MainSG.tasks)
    else:
        await c.answer(localization.get_text("error_completing_and_deleting_task", locale), show_alert=True)

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
        Button(Format("{back}"), id="back", on_click=lambda c, b, m: m.switch_to(MainSG.tasks)),
        state=MainSG.create_task,
        getter=get_create_task
    ),
    Window(
        Format("{enter_task_description}"),
        MessageInput(on_task_description),
        Button(Format("{back}"), id="back", on_click=lambda c, b, m: m.switch_to(MainSG.tasks)),
        state=MainSG.create_task_description,
        getter=get_task_description
    ),
    Window(
        Format("{enter_task_due_date}"),
        MessageInput(on_task_due_date),
        Button(Format("{back}"), id="back", on_click=lambda c, b, m: m.switch_to(MainSG.tasks)),
        state=MainSG.create_task_due_date,
        getter=get_task_due_date
    ),
    Window(
        Format("{enter_task_categories}"),
        MessageInput(on_task_categories),
        Button(Format("{back}"), id="back", on_click=lambda c, b, m: m.switch_to(MainSG.tasks)),
        state=MainSG.create_task_categories,
        getter=get_task_categories
    ),
    Window(
        Format("{task_details}: {task[title]}"),
        Format("{task_description}: {task[description]}"),
        Format("{task_due_date}: {task[due_date]}"),
        Format("{task_categories}: {categories}"),
        Button(Format("{comments}"), id="comments", on_click=lambda c, b, m: m.switch_to(MainSG.comments)),
        Button(Format("{assign_categories_title}"), id="assign_categories_title", on_click=lambda c, b, m: m.switch_to(MainSG.assign_categories)),
        Button(Format("{update_task_emoji}"), id="update_task_emoji", on_click=lambda c, b, m: m.switch_to(MainSG.update_task_title)),
        Button(Format("{complete_and_delete_task_emoji}"), id="complete_and_delete_task_emoji", on_click=on_complete_and_delete_task),
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
                on_click=on_category_del
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
        Button(Format("{back}"), id="back", on_click=lambda c, b, m: m.switch_to(MainSG.categories)),
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
    ),
    Window(
        Format("{assign_categories_title}"),
        Group(
            Select(
                Format("{item[name]}"),
                id="categories_select",
                item_id_getter=lambda x: x["id"],
                items="categories",
                on_click=on_category_selected,
            ),
            width=1
        ),
        Button(Format("{save}"), id="save_categories", on_click=on_save_categories),
        Button(Format("{back}"), id="back", on_click=lambda c, b, m: m.switch_to(MainSG.task_details)),
        state=MainSG.assign_categories,
        getter=get_categories_for_assignment
    ),
    Window(
        Format("{enter_new_title}"),
        MessageInput(on_update_title),
        Button(Format("{back}"), id="back", on_click=lambda c, b, m: m.switch_to(MainSG.task_details)),
        state=MainSG.update_task_title,
        getter=get_update_title
    ),
    Window(
        Format("{enter_new_description}"),
        MessageInput(on_update_description),
        Button(Format("{back}"), id="back", on_click=lambda c, b, m: m.switch_to(MainSG.task_details)),
        state=MainSG.update_task_description,
        getter=get_update_description
    ),
    Window(
        Format("{enter_new_due_date}"),
        MessageInput(on_update_due_date),
        Button(Format("{back}"), id="back", on_click=lambda c, b, m: m.switch_to(MainSG.task_details)),
        state=MainSG.update_task_due_date,
        getter=get_update_due_date
    )
)