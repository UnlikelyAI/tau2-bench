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
