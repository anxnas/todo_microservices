from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.input import MessageInput
from services.fastapi_api import get_comments, create_comment
from utils.i18n import _

class CommentDialog(StatesGroup):
    MAIN_MENU = State()
    VIEW_COMMENTS = State()
    CREATE_COMMENT = State()
    ENTER_TASK_ID = State()
    ENTER_COMMENT = State()

async def get_comments_data(dialog_manager: DialogManager, **kwargs):
    task_id = dialog_manager.current_context().dialog_data.get("task_id")
    if task_id:
        comments = await get_comments(task_id)
        return {"comments": [f"{comment['id']}. {comment['content']}" for comment in comments]}
    return {"comments": []}

async def on_task_id_entered(message: Message, dialog: Dialog, manager: DialogManager):
    manager.current_context().dialog_data["task_id"] = int(message.text)
    await dialog.next(manager)

async def on_comment_entered(message: Message, dialog: Dialog, manager: DialogManager):
    task_id = manager.current_context().dialog_data["task_id"]
    comment = await create_comment(task_id, message.text)
    await message.answer(_("new_comment_created").format(content=comment['content']))
    await manager.done()

comment_dialog = Dialog(
    Window(
        Const(_("comment_menu")),
        Button(Const(_("view_comments")), id="view_comments", state=CommentDialog.VIEW_COMMENTS),
        Button(Const(_("create_comment")), id="create_comment", state=CommentDialog.CREATE_COMMENT),
        state=CommentDialog.MAIN_MENU,
    ),
    Window(
        Const(_("enter_task_id_for_comments")),
        MessageInput(on_task_id_entered),
        state=CommentDialog.ENTER_TASK_ID,
    ),
    Window(
        Format("{comments}"),
        Button(Const(_("back")), id="back", state=CommentDialog.MAIN_MENU),
        state=CommentDialog.VIEW_COMMENTS,
        getter=get_comments_data,
    ),
    Window(
        Const(_("enter_comment_text")),
        MessageInput(on_comment_entered),
        state=CommentDialog.ENTER_COMMENT,
    ),
)

def register_comment_handlers(dp: Dispatcher):
    dp.include_router(comment_dialog)