"""Toolkit for the financial advice domain."""

import json
from typing import Literal
from tau2.environment.toolkit import ToolKitBase, ToolType, is_tool
from tau2.domains.financial_advice.data_model import FinancialAdviceDB


class FinancialAdviceTools(ToolKitBase):  # Tools
    """All the tools for the financial advice domain."""

    def __init__(self, db: FinancialAdviceDB) -> None:
        """
        Initialize the financial advice tools with a database instance.

        Args:
            db: The financial advice database containing user information.
        """
        super().__init__(db)

    @is_tool(ToolType.WRITE)
    def update_recommended_product(
        self,
        product_name: Literal[
            "Share Dealing Account",
            "Fixed Rate Cash ISA",
            "Monthly Saver",
            "Club Lloyds Advantage Saver ISA",
            "Ready Made Pension",
            "Self Invested Personal Pension",
            "Ready Made Investment",
            "Ready Made Investment ISA",
            "Share Dealing ISA",
            "Easy Saver",
        ],
    ) -> str:
        """
        Add a product recommendation to the users database. You MUST call this tool as soon as you have a product recommendation for the user.
        Only call this when giving the product recommendation specifically, it should NOT be called if the user is requesting information about products.
        Args:
            product_name: The name of the product being recommended.
        Returns:
            A confirmation message indicating the recommendation has been updated.
        Raises:
            ValueError: If user is not found or product name is invalid.
        """

        # Validate product name against known products
        valid_products = [
            "Share Dealing Account",
            "Fixed Rate Cash ISA",
            "Monthly Saver",
            "Club Lloyds Advantage Saver ISA",
            "Ready Made Pension",
            "Self Invested Personal Pension",
            "Ready Made Investment",
            "Ready Made Investment ISA",
            "Share Dealing ISA",
            "Easy Saver",
        ]

        if product_name not in valid_products:
            raise ValueError(
                f"Invalid product name: {product_name}. Valid products are: {', '.join(valid_products)}"
            )
        # Update the recommended product
        success = self.db.update_user_recommendation(product_name)
        if not success:
            raise ValueError(
                f"Failed to update recommendation for user {self.db.current_user_id}"
            )

        return f"Successfully updated recommended product for {self.db.current_user_id} to: {product_name}"


if __name__ == "__main__":
    # Load the database for testing
    import json

    with open("data/tau2/domains/financial-advice/db.json", "r") as f:
        db_data = json.load(f)

    # Convert to proper data model
    db = FinancialAdviceDB()
    for user_id, user_data in db_data["users"].items():
        from tau2.domains.financial_advice.data_model import (
            User,
            UserName,
            UserAddress,
            FinancialProfile,
        )

        user = User(
            user_id=user_id,
            name=UserName(**user_data["name"]),
            address=UserAddress(**user_data["address"]),
            email=user_data["email"],
            dob=user_data["dob"],
            financial_profile=FinancialProfile(**user_data["financial_profile"]),
            expected_recommended_product=user_data["expected_recommended_product"],
            recommended_product=user_data.get("recommended_product", ""),
        )
        db.add_user(user)

    financial_advice = FinancialAdviceTools(db)
    print(financial_advice.get_statistics())
