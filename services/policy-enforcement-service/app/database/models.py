from .basemodel import Base


Pages = None

def as_dict(obj):
    data = obj.__dict__
    data.pop('_sa_instance_state')
    return data

def init_existing_models(base_map):
    global Pages

    Pages = base_map.classes.pages

    for c in [Pages]:
        c.as_dict = as_dict