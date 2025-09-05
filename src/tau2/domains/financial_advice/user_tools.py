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
    def update_recommended_product(
        self,
        user_id: str,
        product_name: Literal[
            "Share Dealing Account",
            "Fixed Rate Cash ISA",
            "Monthly Saver",
        ],
    ) -> str:
        """
        Update your recommended product. This should be called when the assistant
        makes an explicit product recommendation based on the user's financial profile and the policy criteria.

        Args:
            user_id: The user ID to update the recommendation for.
            product_name: The name of the product being recommended.

        Returns:
            A confirmation message indicating the recommendation has been updated.

        Raises:
            ValueError: If user is not found or product name is invalid.
        """
        print(f"Updating recommended product for user {user_id} to {product_name}")

        user = self._get_user(user_id)

        # Validate product name against known products
        valid_products = [
            "Share Dealing ISA",
            "Share Dealing Account",
            "Ready Made Investment ISA",
            "Ready Made General Investment Account",
            "Fixed Rate Cash ISA",
            "Cash ISA",
            "Online Fixed Bond",
            "Monthly Saver",
            "Easy Saver",
        ]

        if product_name not in valid_products:
            raise ValueError(
                f"Invalid product name: {product_name}. Valid products are: {', '.join(valid_products)}"
            )

        # Update the recommended product
        success = self.db.update_user_recommendation(user_id, product_name)
        if not success:
            raise ValueError(f"Failed to update recommendation for user {user_id}")

        return f"Successfully updated recommended product for {user.name.first_name} {user.name.last_name} to: {product_name}"

    @is_tool(ToolType.WRITE)
    def set_current_user_id(self, user_id: str) -> str:
        """
        Set the current user ID.
        """
        self.db.current_user_id = user_id
        return f"Current user ID set to {user_id}"

    # Assertion tools for testing
    def assert_my_financial_profile(self, user_id: str, **profile_attributes) -> bool:
        """
        Assert that the user's financial profile matches specific criteria.

        Args:
            user_id: The user ID to check.
            **profile_attributes: Key-value pairs of financial profile attributes to check.

        Returns:
            True if all specified attributes match, False otherwise.
        """
        user = self._get_user(user_id)
        financial_profile = user.financial_profile

        for attr_name, expected_value in profile_attributes.items():
            if not hasattr(financial_profile, attr_name):
                return False
            if getattr(financial_profile, attr_name) != expected_value:
                return False

        return True

    def assert_recommendation_matches_expected(self, user_id: str, **kwargs) -> bool:
        """
        Assert that a user's current recommendation matches their expected recommendation.

        Args:
            user_id: The user ID to check.

        Returns:
            True if current recommendation matches expected, False otherwise.
        """
        user = self._get_user(user_id)
        return user.recommended_product == user.expected_recommended_product
