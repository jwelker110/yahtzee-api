from protorpc import messages


class ReauthForm(messages.Message):
    jwt_token = messages.StringField(1)


class UserAuthFormRequest(messages.Message):
    jwt_token = messages.StringField(1, required=True)
    auth_code = messages.StringField(2, required=True)


class UserAuthFormResponse(messages.Message):
    jwt_token = messages.StringField(1, required=True)
