import typing_extensions

from acme_client.apis.tags import TagValues
from acme_client.apis.tags.pet_api import PetApi
from acme_client.apis.tags.user_api import UserApi
from acme_client.apis.tags.store_api import StoreApi
from acme_client.apis.tags.miscellaneous_api import MiscellaneousApi

TagToApi = typing_extensions.TypedDict(
    'TagToApi',
    {
        TagValues.PET: PetApi,
        TagValues.USER: UserApi,
        TagValues.STORE: StoreApi,
        TagValues.MISCELLANEOUS: MiscellaneousApi,
    }
)

tag_to_api = TagToApi(
    {
        TagValues.PET: PetApi,
        TagValues.USER: UserApi,
        TagValues.STORE: StoreApi,
        TagValues.MISCELLANEOUS: MiscellaneousApi,
    }
)
