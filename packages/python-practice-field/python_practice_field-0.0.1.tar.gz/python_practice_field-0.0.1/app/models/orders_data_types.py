"""Data types for application."""
from enum import Enum
from typing import Annotated, Optional

from fastapi import Body, Query
from pydantic import BaseModel, ConfigDict, Extra, Field, confloat, validator

from app.functions.common import read_txt_to_list

DEFAULT_PRODUCTS_SUBSTRS_FILE = 'default_products_substrs.txt'
DEFAULT_PRODUCTS_SUBSTRS: list = read_txt_to_list(DEFAULT_PRODUCTS_SUBSTRS_FILE)

Charity = Optional[
    Annotated[
        int,
        Query(
            title='Optional money for charity',
            description='Money for charity',
            ge=1,
            include_in_schema=True,
            deprecated=False,
        )]]


class Stores(Enum):
    """Valid stores names."""

    apple = 'apple'


class ProductsInfo(BaseModel):
    """Check for custom product's info passed to post request."""

    product_name: str = Field(max_length=20)
    price: confloat(gt=1)  # type: ignore

    @validator('product_name', pre=True)
    def product_should_contain_default_substr(cls, product_name: str) -> str:
        """
        Check if information about a product contains default substrings.

        :param product_name: checked param
        :raises ValueError: if product_name doesn't contain default substr
        :returns: product_name without changes if condition is passed
        """
        name_contains_valid_substr = any(substring in product_name.lower() for substring in DEFAULT_PRODUCTS_SUBSTRS)

        if not name_contains_valid_substr:
            raise ValueError(
                'Product_name should involve default_products_substrs: {default_products_substrs}'.format(
                    default_products_substrs=DEFAULT_PRODUCTS_SUBSTRS,
                ),
            )
        return product_name

    model_config = ConfigDict(extra=Extra.allow)


class StorePositions(BaseModel):
    """Request body data type."""

    products_info: Annotated[
        list[ProductsInfo],
        Body(
            title='List of products names with corresponding prices',
            description='Dict to generate random data from',
            examples=[
                {'products_info': [
                    {'product_name': 'MacBook Pro', 'price': 1999.99},
                    {'product_name': 'iPad Air', 'price': 899.99},
                ]}],
            embed=False,
        )]
