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
        Add a product recommendation to the user's database. You MUST call this tool as soon as you have a product recommendation for the user.
        You can recommend multiple products by calling this tool multiple times with different product names.
        Only call this when giving the product recommendation specifically, it should NOT be called if the user is requesting information about products.

        Args:
            product_name: The name of the product being recommended.

        Returns:
            A confirmation message indicating the recommendation has been added.

        Raises:
            ValueError: If user is not found or product name is invalid.
        """

        # Validate product name against known products
        valid_products = [
            "Monthly Saver",
            "Easy Saver",
            "Cash ISA Saver",
            "Club Lloyds Advantage Saver",
            "Club Lloyds Advantage Saver ISA",
            "Club Lloyds Monthly Saver",
            "Club Lloyds Saver",
            "Fixed Rate Cash ISA",
            "Share Dealing ISA",
            "Online Fixed Bonds",
            "Ready Made Pension",
            "Ready Made Investment",
            "Ready Made Investment ISA",
            "Self Invested Personal Pension",
            "Share Dealing Account",
            "Lend a Hand Fixed Savings Account",
        ]

        if product_name not in valid_products:
            raise ValueError(
                f"Invalid product name: {product_name}. Valid products are: {', '.join(valid_products)}"
            )

        # Get current user
        if self.db.current_user_id not in self.db.users:
            raise ValueError(
                f"Failed to update recommendation - user {self.db.current_user_id} not found"
            )

        user = self.db.users[self.db.current_user_id]

        # Check if product already recommended
        already_recommended = product_name in user.recommended_products

        # Add the recommended product
        success = self.db.update_user_recommendation(product_name)

        if not success:
            raise ValueError(
                f"Failed to update recommendation for user {self.db.current_user_id}"
            )

        # Build response message
        if already_recommended:
            message = f"Product '{product_name}' was already recommended for {self.db.current_user_id}."
        else:
            message = f"Successfully added '{product_name}' to recommendations for {self.db.current_user_id}."

        # Show all current recommendations
        all_recommendations = user.recommended_products
        if len(all_recommendations) > 1:
            message += f" Total recommended products: {', '.join(all_recommendations)}"

        return message


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
        )

        user = User(
            user_id=user_id,
            name=UserName(**user_data["name"]),
            address=UserAddress(**user_data["address"]),
            email=user_data["email"],
            dob=user_data["dob"],
            recommended_products=user_data.get("recommended_products", []),
        )
        db.add_user(user)

    financial_advice = FinancialAdviceTools(db)
    print(financial_advice.get_statistics())
