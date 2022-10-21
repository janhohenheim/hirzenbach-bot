from persistance import Data, init_database, add_sticker, subscribe_morning, subscribe_stickers, append_to_memory


def migrate():
    data = Data.read()
    _migrate_stickers(data)
    _migrate_sticker_subscribers(data)
    _migrate_morning_subscribers(data)
    _migrate_memory(data)


def _migrate_stickers(data: Data):
    for sticker in data.sticker_pool:
        add_sticker(sticker)


def _migrate_sticker_subscribers(data: Data):
    for chat_id in data.sticker_subscribers:
        subscribe_stickers(chat_id)


def _migrate_morning_subscribers(data: Data):
    for chat_id in data.morning_subscribers:
        subscribe_morning(chat_id)


def _migrate_memory(data: Data):
    for chat_id, messages in data.memory.items():
        for message in messages:
            append_to_memory(chat_id, message)


if __name__ == '__main__':
    init_database()
    migrate()
