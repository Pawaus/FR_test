from ninja import Schema, Field


class ClientCreate(Schema):
    phone: str = "71231231212"
    code_operator: str = "123"
    tag: str = "tag_user_ad"
    time_zone: str = "utc+0"


class ClientUpdate(Schema):
    phone: str = "71231231212"
    code_operator: str = None
    tag: str = None
    time_zone: str = None



class ClientDelete(Schema):
    phone: str = "71231231212"



class ClientDefaultResponse(Schema):
    status: str = "ok"

