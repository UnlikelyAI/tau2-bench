"""Toolkit for the airline reservation system."""

from copy import deepcopy
from typing import List, Optional

from loguru import logger

from tau2.environment.toolkit import ToolKitBase, ToolType, is_tool
from tau2.domains.financial_advice.data_model import Product


class FinancialAdviceTools(ToolKitBase):  # Tools
    """All the tools for the financial advice domain."""

    def __init__(self) -> None:
        super().__init__()

    # TODO: Implement the product information tool
    # def _get_product(self, product_id: str) -> Product:
    #     """
    #     Get the details of a product.

    #     Args:
    #         product_id: The product ID, such as '1'.

    #     Returns:
    #         The product details.
    #     """
    #     return Product(id=product_id, name="Product 1", detail="Detail 1")

    # @is_tool(ToolType.READ)
    # def get_product_details(self, product_id: str) -> Product:
    #     """
    #     Get the details of a product.

    #     Args:
    #         product_id: The product ID, such as '1'.

    #     Returns:
    #         The product details.

    #     Raises:
    #         ValueError: If the product is not found.
    #     """
    #     return self._get_product(product_id)


if __name__ == "__main__":
    financial_advice = FinancialAdviceTools()
    print(financial_advice.get_statistics())
