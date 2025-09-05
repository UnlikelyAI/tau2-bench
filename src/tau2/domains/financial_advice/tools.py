"""Toolkit for the financial advice domain."""

import os
import json
from typing import Literal
from tau2.environment.toolkit import ToolKitBase, ToolType, is_tool
from tau2.domains.financial_advice.data_model import FinancialAdviceDB
from tau2.domains.financial_advice.utils import (
    PRODUCT_FILES,
    KNOWLEDGE_BASE_PATH,
    load_product_file_contents,
)
from openai import OpenAI


def product_files_as_str(product_file_contents: list[str]) -> str:
    s = ""
    for i, file_content in enumerate(product_file_contents):
        s += f"""
Document {i+1}:
```markdown
{file_content}
```
"""
    return s


product_file_contents = load_product_file_contents(KNOWLEDGE_BASE_PATH, PRODUCT_FILES)
product_files_str = product_files_as_str(product_file_contents)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


class FinancialAdviceTools(ToolKitBase):  # Tools
    """All the tools for the financial advice domain."""

    def __init__(self, db: FinancialAdviceDB) -> None:
        """
        Initialize the financial advice tools with a database instance.

        Args:
            db: The financial advice database containing user information.
        """
        super().__init__(db)

    def _get_product(self, query: str) -> str:
        """
        Lookup product information from the Lloyds Bank website on the topic of the query.

        Args:
            query: The query to get the product details.

        Returns:
            A string that contains the product details.
        """

        documents = f"""
Here is the set of documents that you can use to provide your guidance:
{product_files_str}
        """
        instructions = f"""
You are an assistant to a finaicial advisor for Lloyds Bank customers.
Your goal is to retrieve guidance i.e. accurate and cited information about financial products and related topics for Lloyds bank, that is:
- relevant to the advisor's query
- fair, clear, not-misleading in order to be compliant with FCA regulations (COBS)
- sourced ONLY from the set of documents provided to you below.

Process to follow:
- In order to retrieve any and all of the relevant information accurately, go through each of the documents provided below, understanding their topic and content and then carefully retrieve all the information that may be useful to respond to the advisor.
- You should only provide fair, clear and not-misleading factual information, making sure that any key details are verbatim from the source documents.
- You must always cite the URL from the source documents you use in your response.
- Always provide your best guess of cited relevant information in your response, don't respond back with a question or a comment.
        """
        messages = [
            {"role": "system", "content": instructions},
            {"role": "developer", "content": documents},
            {"role": "user", "content": query},
        ]
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.responses.create(model="gpt-4o", input=messages)
        return response.output[0].content[-1].text

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

    @is_tool(ToolType.READ)
    def get_product_details(self, query: str) -> str:
        """
        Lookup product information from the Lloyds Bank website on the topic of the query.

        Args:
            query: The query to get the product details.

        Returns:
            A string that contains the product details.
        """
        return self._get_product(query)

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
        Update the recommended product of the current user. This should be called when the assistant
        makes an explicit product recommendation based on the user's financial profile and the policy criteria.

        Only call this when giving the product recommendation specifically, it should NOT be called if the user is requesting information about products.

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

    @is_tool(ToolType.READ)
    def get_current_user_id(self) -> str:
        """
        Get the current user ID.
        """
        return self.db.current_user_id


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
