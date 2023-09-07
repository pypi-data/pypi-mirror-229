from acme_client.paths.pet.put import ApiForput
from acme_client.paths.pet.post import ApiForpost


class Pet(
    ApiForput,
    ApiForpost,
):
    pass
