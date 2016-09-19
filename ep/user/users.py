import endpoints

from protorpc import messages, remote
from ep.endpoint_api import yahtzee
from messages import UserAllRequestForm, UserAllResponseForm, UserForm
from models import User


@yahtzee.api_class("user")
class UserAllHandler(remote.Service):
    @endpoints.method(endpoints.ResourceContainer(
        offset=messages.IntegerField(1, default=0)
    ),
                      UserAllResponseForm,
                      name="retrieve_users",
                      path="user/all",
                      http_method="GET")
    def retrieve_users(self, request):
        """
        Return 10 users starting from the provided offset, or 0
        """
        offset = request.offset

        try:
            users = User.query().fetch(offset=offset, limit=10)
            return UserAllResponseForm(
                users=[UserForm(
                    username=user.username,
                    user_key=user.key.urlsafe()
                ) for user in users]
            )
        except Exception as e:
            print e.message
            raise endpoints.InternalServerErrorException('An error occurred while retrieving users')
