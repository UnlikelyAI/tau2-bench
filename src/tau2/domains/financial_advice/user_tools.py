"""User tools for the financial advice domain."""

from typing import List
from tau2.environment.toolkit import ToolKitBase, ToolType, is_tool
from tau2.domains.financial_advice.data_model import FinancialAdviceDB


class FinancialAdviceUserTools(ToolKitBase):
    """
    Provides methods for users to access their financial situation and preferences
    for use when answering questions from the financial advisor assistant.
    """

    db: FinancialAdviceDB

    def __init__(self, db: FinancialAdviceDB) -> None:
        """
        Initialize the user tools with a database instance.

        Args:
            db: The financial advice database containing user information.
        """
        super().__init__(db)

    def _get_user(self, user_id: str):
        """
        Get user information from the database.

        Args:
            user_id: The user ID to look up.

        Returns:
            User information object.

        Raises:
            ValueError: If user is not found.
        """
        user = self.db.get_user_by_id(user_id)
        if user is None:
            raise ValueError(f"User {user_id} not found")
        return user

    @is_tool(ToolType.WRITE)
    def set_current_user_id(self, user_id: str) -> str:
        """
        Set the current user ID.

        Args:
            user_id: The user ID to set as current.

        Returns:
            Confirmation message.
        """
        self.db.current_user_id = user_id
        return f"Current user ID set to {user_id}"

    @is_tool(ToolType.READ)
    def check_recommendations(self, user_id: str) -> list[str]:
        """
        Check if the user has any recommendations.
        """
        user = self._get_user(user_id)
        return user.recommended_products

    def assert_recommendations(
        self, user_id: str, expected_products: List[str], **kwargs
    ) -> bool:
        """
        Assert that a user's recommended products list exactly matches the expected products.
        The lists must contain the same items (order doesn't matter), but no extra or missing items.

        Args:
            user_id: The user ID to check.
            expected_products: List of products that should exactly match the recommendations list.

        Returns:
            True if the recommended products exactly match expected products (same items, any order), False otherwise.
        """
        user = self._get_user(user_id)

        expected_products_lower = [product.lower() for product in expected_products]
        user_products_lower = [product.lower() for product in user.recommended_products]

        # Convert both lists to sets to compare regardless of order
        return set(user_products_lower) == set(expected_products_lower)
