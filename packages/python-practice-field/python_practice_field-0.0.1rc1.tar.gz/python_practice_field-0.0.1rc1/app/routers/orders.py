
"""
Methods that generate random basket.

DESCRIPTION:
* Get for basket based on preset values
* Post for one based on user requestbody
"""
from fastapi import APIRouter

from app.functions.methods_functions import generate_random_order
from app.models.orders_data_types import Charity, StorePositions, Stores

router = APIRouter()


@router.get('/orders/{store}')
async def read_items(store: Stores, charity: Charity = None) -> dict:
    """
    Get request returning random busket.

    :param store: acceptable store name
    :param charity: charity donation
    :returns: random order busket.
    """
    if store is Stores.apple:
        response = generate_random_order()

    if charity:
        response.update({'charity': charity})

    return response


@router.post('/orders/{store}')
async def read_custom_items(store: Stores, requestbody: StorePositions, charity: Charity = None) -> dict:
    """
    Get request returning random busket from data sent by user.

    :param store: acceptable store name
    :param charity: charity donation
    :param requestbody: user custom busket to generate order from
    :returns: random order busket.
    """
    if store is Stores.apple:
        response = generate_random_order(requestbody)

    if charity:
        response.update({'charity': charity})

    return response
