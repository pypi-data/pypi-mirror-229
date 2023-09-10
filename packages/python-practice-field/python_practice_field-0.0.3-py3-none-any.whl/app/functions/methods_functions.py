"""Functions used to make responses."""
import secrets

from app.functions.common import read_json_to_dict
from app.models.orders_data_types import StorePositions

DEFAULT_STORE_POSITIONS_FILE = 'default_store_positions.json'
DEFAULT_APPLE_STORE_POSITIONS = StorePositions(**read_json_to_dict(DEFAULT_STORE_POSITIONS_FILE))


def generate_random_order(products_info: StorePositions = DEFAULT_APPLE_STORE_POSITIONS) -> dict:
    """
    Parse dictionary and generate new one with random quantities and total price.

    :param products_info: dictionary that contains store positions
    :returns: random basket generated from products_info
    """
    products_info_dumped = products_info.dict()
    store_positions = {}

    for dict_element in products_info_dumped['products_info']:
        store_positions.update({dict_element['product_name']: dict_element['price']})

    product_name = secrets.choice(list(store_positions.keys()))
    price_per_item = store_positions[product_name]
    quantity = secrets.randbelow(100) + 1
    total_product_price = quantity * price_per_item

    return {
        'product_name': product_name,
        'price_per_item': price_per_item,
        'quantity': quantity,
        'total_price': total_product_price,
    }


if __name__ == '__main__':
    generate_random_order()
