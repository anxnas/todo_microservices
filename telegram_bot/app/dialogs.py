from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Button, Select, Back,Group
from aiogram_dialog.widgets.text import Const, Format, Jinja
from aiogram_dialog.widgets.input import MessageInput
from states import MainSG
from handlers import (
    on_task_selected, on_language_selected, on_complete_and_delete_task,
    on_create_task, on_task_description, on_task_due_date, on_task_categories,
    on_create_category, on_create_comment, on_delete_comment, on_category_del,
    on_category_selected, on_save_categories, on_update_title, on_update_description,
    on_update_due_date
)
from getters import (
    check_user, get_tasks, get_task_details, get_categories, get_categories_for_assignment,
    get_comments, get_create_comment, get_create_category, get_create_task,
    get_task_description, get_task_due_date, get_task_categories, get_update_title,
    get_update_description, get_update_due_date
)

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