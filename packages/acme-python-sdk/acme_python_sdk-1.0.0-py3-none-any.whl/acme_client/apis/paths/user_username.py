from acme_client.paths.user_username.get import ApiForget
from acme_client.paths.user_username.put import ApiForput
from acme_client.paths.user_username.delete import ApiFordelete


class UserUsername(
    ApiForget,
    ApiForput,
    ApiFordelete,
):
    pass
