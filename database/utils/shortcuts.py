import typing as t

from loguru import logger

from database import utils as db
from database.models import BaseModel
from database.models import Chat
from database.models import Storage
from database.models import Student
from services.exceptions import ChatNotFound
from services.logger.config import config

logger.configure(**config)


def generate_list(data) -> t.List[BaseModel]:
    return [item for item in data]


def update_admin_storage(admin_id: int, **kwargs) -> Storage:
    """
    Обновляет хранилище администратора и возвращает объект хранилища
    Args:
        admin_id: идентификатор администратора
        **kwargs: поля для обновления

    Returns:
        Storage: объект хранилища
    """
    store = db.admin.get_admin_storage(admin_id).update(**kwargs)
    store.execute()
    logger.debug(f"Хранилище id{admin_id} обновлено с {kwargs}")
    return store


def clear_admin_storage(admin_id: int) -> Storage:
    """
    Очищает хранилище администратора
    Args:
        admin_id: идентификатор администратора

    Returns:
        Storage: объект хранилища
    """
    return update_admin_storage(
        admin_id,
        state_id=1,
        selected_students="",
        text="",
        attaches="",
        confirm_message="",
    )


def get_list_of_calling_students(admin_id: int) -> t.List[int]:
    """
    Возвращает список призываемых студентов из хранилища администратора admin_id
    Args:
        admin_id: идентификатор администратора

    Returns:
        list[int]: список призываемых
    """
    store = db.admin.get_admin_storage(admin_id)
    students = store.selected_students
    return list(map(int, filter(bool, students.split(","))))


def update_calling_list(admin_id: int, calling_list: list) -> Storage:
    """
    Изменяет список призыва
    Args:
        admin_id: идентификатор администратора
        calling_list: список призыва для замены

    Returns:
        Storage: хранилище администратора
    """
    return update_admin_storage(
        admin_id, selected_students=",".join(map(str, calling_list))
    )


def pop_student_from_calling_list(admin_id: int, student_id: int) -> Storage:
    """
    Удаляет студента из списка призываемых студентов
    Args:
        admin_id: идентификатор администратора
        student_id: идентфикатор удаляемого студента

    Returns:
        Storage: хранилище администратора
    """
    cl = get_list_of_calling_students(admin_id)
    cl.remove(student_id)
    return update_calling_list(admin_id, cl)


def add_student_to_calling_list(admin_id: int, student_id: int) -> Storage:
    """
    Добавляет студента в список призываемых студентов
    Args:
        admin_id: идентификатор администратора
        student_id: идентфикатор добавляемого студента

    Returns:
        Storage: хранилище администратора
    """
    cl = get_list_of_calling_students(admin_id)
    cl.append(student_id)
    return update_calling_list(admin_id, cl)


def get_active_chat(admin_id: int) -> Chat:
    """
    Получает идентификатор активного чата конкретного администратора
    Args:
        admin_id: идентификатор администратора

    Returns:
        Chat: объект активного чата
    """
    store = db.admin.get_admin_storage(admin_id)
    return Chat.get(
        chat_type=store.current_chat,
        group_id=Student.get(id=store.id).group_id,
    )


def invert_names_usage(admin_id: int) -> Storage:
    """
    Изменяет использование имен у администратора
    Args:
        admin_id: идентификатор администратора

    Returns:
        Storage: объект хранилища
    """
    store = db.admin.get_admin_storage(admin_id)
    state = not store.names_usage
    return update_admin_storage(admin_id, names_usage=state)


def invert_current_chat(admin_id: int) -> Storage:
    """
    Изменяет активный чат администратора
    Args:
        admin_id: идентификатор администратора

    Returns:
        Storage: объект хранилища
    """
    active_chat = get_active_chat(admin_id)
    store = db.admin.get_admin_storage(admin_id)
    group_id = Student.get_by_id(store.id).group_id
    another_type = abs(active_chat.chat_type.id - 1)
    another_chat = Chat.get(group_id=group_id, chat_type=another_type)
    if another_chat is not None:
        return update_admin_storage(admin_id, current_chat=another_type)
    else:
        raise ChatNotFound(
            f"У группы {group_id} не зарегистрирован" f"{another_chat} чат"
        )
