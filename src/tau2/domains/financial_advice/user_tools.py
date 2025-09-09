"""User tools for the financial advice domain."""

from typing import Literal
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

    def assert_recommendation(
        self, user_id: str, expected_product: str, **kwargs
    ) -> bool:
        """
        Assert that a user's current recommendation matches their expected recommendation.

        Args:
            user_id: The user ID to check.

        Returns:
            True if current recommendation matches expected, False otherwise.
        """
        user = self._get_user(user_id)
        return user.recommended_product == expected_product
