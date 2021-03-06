from database.models import State
from services.exceptions import BotStateNotFound


def get_id_of_state(description: str) -> int:
    """
    Возвращает идентификатор состояния бота по его описанию.

    Args:
        description: описание статуса бота

    Returns:
        int: идентфикатор статуса бота

    Raises:
        BotStateNotFound: если переданный статус бота не был найден в БД
    """
    state = State.get_or_none(description=description)
    if state is not None:
        return state.id
    raise BotStateNotFound(f'Статус "{description}" не существует')
