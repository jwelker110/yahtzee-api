from protorpc import messages


class ReauthForm(messages.Message):
    jwt_token = messages.StringField(1, required=True)


class UserAuthFormRequest(messages.Message):
    auth_code = messages.StringField(1, required=True)


class UserAuthFormResponse(messages.Message):
    jwt_token = messages.StringField(1, required=True)
