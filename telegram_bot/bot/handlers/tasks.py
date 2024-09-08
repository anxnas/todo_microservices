from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.input import MessageInput
from services.django_api import get_tasks, create_task, get_categories
from utils.i18n import _

# Определение состояний диалога
class TaskDialog(StatesGroup):
    MAIN_MENU = State()
    VIEW_TASKS = State()
    CREATE_TASK = State()
    ENTER_TITLE = State()
    ENTER_DESCRIPTION = State()
    CHOOSE_CATEGORY = State()

# Функции для получения данных
async def get_tasks_data(dialog_manager: DialogManager, **kwargs):
    user_id = dialog_manager.event.from_user.id
    tasks = await get_tasks(user_id)
    return {
        "tasks": [f"{task['id']}. {task['title']} ({task['category']}) - {task['created_at']}" for task in tasks]
    }

async def get_categories_data(dialog_manager: DialogManager, **kwargs):
    user_id = dialog_manager.event.from_user.id
    categories = await get_categories(user_id)
    return {"categories": categories}

# Обработчики ввода
async def on_title_entered(message: Message, dialog: Dialog, manager: DialogManager):
    manager.current_context().dialog_data["title"] = message.text
    await dialog.next(manager)

async def on_description_entered(message: Message, dialog: Dialog, manager: DialogManager):
    manager.current_context().dialog_data["description"] = message.text
    await dialog.next(manager)

async def on_category_selected(callback: CallbackQuery, button: Button, manager: DialogManager):
    user_id = callback.from_user.id
    dialog_data = manager.current_context().dialog_data
    task = await create_task(
        user_id,
        dialog_data["title"],
        dialog_data["description"],
        button.widget_id
    )
    await callback.message.answer(_("new_task_created").format(title=task['title']))
    await manager.done()

# Определение диалога
task_dialog = Dialog(
    Window(
        Const(_("main_menu")),
        Button(Const(_("view_tasks")), id="view_tasks", state=TaskDialog.VIEW_TASKS),
        Button(Const(_("create_task")), id="create_task", state=TaskDialog.CREATE_TASK),
        state=TaskDialog.MAIN_MENU,
    ),
    Window(
        Format("{tasks}"),
        Button(Const(_("back")), id="back", state=TaskDialog.MAIN_MENU),
        state=TaskDialog.VIEW_TASKS,
        getter=get_tasks_data,
    ),
    Window(
        Const(_("enter_task_title")),
        MessageInput(on_title_entered),
        state=TaskDialog.ENTER_TITLE,
    ),
    Window(
        Const(_("enter_task_description")),
        MessageInput(on_description_entered),
        state=TaskDialog.ENTER_DESCRIPTION,
    ),
    Window(
        Const(_("choose_category")),
        Format("{categories}"),
        Button(Const(_("back")), id="back", state=TaskDialog.MAIN_MENU),
        state=TaskDialog.CHOOSE_CATEGORY,
        getter=get_categories_data,
    ),
)

# Регистрация диалога
def register_task_handlers(dp: Dispatcher):
    dp.include_router(task_dialog)