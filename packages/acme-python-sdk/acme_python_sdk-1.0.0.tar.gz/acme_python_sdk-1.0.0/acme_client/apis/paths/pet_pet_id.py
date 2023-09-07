from acme_client.paths.pet_pet_id.get import ApiForget
from acme_client.paths.pet_pet_id.post import ApiForpost
from acme_client.paths.pet_pet_id.delete import ApiFordelete


class PetPetId(
    ApiForget,
    ApiForpost,
    ApiFordelete,
):
    pass
