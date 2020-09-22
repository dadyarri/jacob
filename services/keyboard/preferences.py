import typing as t

import requests
from vkwave.bots import Keyboard

from database import utils as db
from database.models import ChatType
from services.keyboard import common

JSONStr = str


def preferences() -> JSONStr:
    """
    Возвращает клавиатуру главного окна настроек
    Returns:
        JSONStr: клавиатура
    """
    kb = Keyboard()
    kb.add_text_button("💬 Настроить чаты", payload={"button": "configure_chats"})
    kb.add_row()
    kb.add_text_button("◀️ Назад", payload={"button": "main_menu"})

    return kb.get_keyboard()


async def connected_chats(vk_id: int) -> JSONStr:
    """
    Генерирует клавиатуру со списком подключенных чатов
    Args:
        vk_id: идентификатор пользователя
    Returns:
        JSONStr: клавиатура
    """
    kb = await common.list_of_chats(vk_id)
    chats = db.chats.get_list_of_chats_by_group(vk_id)
    if kb.buttons[-1]:
        kb.add_row()
    if len(chats) < len(db.chats.get_chat_types()):
        kb.add_text_button("➕ Зарегистрировать чат", payload={"button": "reg_chat"})
        kb.add_row()
    kb.add_text_button("◀️ Назад", payload={"button": "settings"})
    return kb.get_keyboard()


def configure_chat(chat_id: int):
    """
    Меню настройки чата

    Args:
        chat_id: Идентфикатор чата

    Returns:
        JSONStr: клавиатура
    """
    kb = Keyboard()
    kb.add_text_button(
        "🗑 Отключить чат", payload={"button": "remove_chat", "chat": chat_id}
    )
    kb.add_row()
    kb.add_text_button(
        "🗂 Индексировать чат", payload={"button": "index_chat", "chat": chat_id}
    )
    kb.add_row()
    kb.add_text_button("◀️ Назад", payload={"button": "configure_chats"})
    return kb.get_keyboard()


def index_chat(
    group_id: int, vk_students: t.List[int], db_students: t.List[int], chat_type: int
) -> JSONStr:
    """
    Меню индексации чата

    Args:
        group_id: Номер группы, в которую нужно добавить студентов
        vk_students: Список студентов, присутствующих в чате
        db_students: Список студентов, присутствующих в БД
        chat_type: Тип чата (используется для возврата на уровень выше)
    Returns:
        JSONStr: Клавиатура
    """
    kb = Keyboard()
    if vk_students:
        query = requests.post(
            "https://dpaste.com/api/v2/",
            data={
                "content": ",".join(map(str, vk_students)),
                "syntax": {"text": "Plain " "text"},
            },
        )
        link = query.text.strip("\n")
        kb.add_text_button(
            "➕ Зарегистрировать студентов",
            payload={
                "button": "register_students",
                "group": group_id,
                "chat_type": chat_type,
                "students": link,
            },
        )
        kb.add_row()
    if db_students:
        query = requests.post(
            "https://dpaste.com/api/v2/",
            data={
                "content": ",".join(map(str, db_students)),
                "syntax": {"text": "Plain text"},
            },
        )
        link = query.text.strip("\n")
        kb.add_text_button(
            "➖ Удалить студентов",
            payload={
                "button": "purge_students",
                "group": group_id,
                "chat_type": chat_type,
                "students": link,
            },
        )
        kb.add_row()
    kb.add_text_button(
        "◀️ Назад",
        payload={"button": "chat", "group": group_id, "chat_type": chat_type},
    )
    return kb.get_keyboard()


def available_chat_types(vk_id: int, chat: int):
    kb = Keyboard()
    chats = db.chats.get_list_of_chats_by_group(vk_id)
    all_chat_types = db.chats.get_chat_types()
    registered_chat_types = [chat.chat_type for chat in chats]

    free_chat_types = [i.id for i in all_chat_types if i not in registered_chat_types]

    group_id = db.admin.get_admin_feud(db.students.get_system_id_of_student(vk_id)).id
    for chat_type in free_chat_types:
        if len(kb.buttons[-1]) == 2:
            kb.add_row()
        obj = ChatType.get(id=chat_type)
        kb.add_text_button(
            obj.description,
            payload={
                "button": "register_chat",
                "chat_type": chat_type,
                "chat": chat,
                "group": group_id,
            },
        )
    if kb.buttons[-1]:
        kb.add_row()
    kb.add_text_button("◀️ Назад", payload={"button": "reg_chat"})
    return kb.get_keyboard()
