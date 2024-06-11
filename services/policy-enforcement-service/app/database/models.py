from .basemodel import Base


Pages = None
Cards = None
Diaries = None
Chats = None
Messages = None
Meetings = None
Records = None

def as_dict(obj):
    data = obj.__dict__
    data.pop('_sa_instance_state')
    return data

def init_existing_models(base_map):
    global Pages, Cards, Diaries, Chats, Messages, Records

    Pages = base_map.classes.pages
    Cards = base_map.classes.cards
    Diaries = base_map.classes.pages_diary
    Chats = base_map.classes.chat
    Messages = base_map.classes.message
    Meetings = base_map.classes.meeting
    Records = base_map.classes.record

    for c in [Pages, Cards, Diaries, Chats, Messages, Meetings, Records]:
        c.as_dict = as_dict