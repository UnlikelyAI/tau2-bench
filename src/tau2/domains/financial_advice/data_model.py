"""Data models for the financial advice domain."""

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import Field

from tau2.domains.financial_advice.utils import FINANCIAL_ADVICE_DB_PATH
from tau2.environment.db import DB
from tau2.utils.pydantic_utils import BaseModelNoExtra


class ProductType(str, Enum):
    """Types of financial products available."""

    SHARE_DEALING_ACCOUNT = "Share Dealing Account"
    FIXED_RATE_CASH_ISA = "Fixed Rate Cash ISA"
    MONTHLY_SAVER = "Monthly Saver"


class UserAddress(BaseModelNoExtra):
    """User's address information."""

    address1: str = Field(description="First line of address")
    address2: Optional[str] = Field(
        None, description="Second line of address (optional)"
    )
    city: str = Field(description="City name")
    country: str = Field(description="Country name")
    postcode: str = Field(description="Postal/ZIP code")


class UserName(BaseModelNoExtra):
    """User's name information."""

    first_name: str = Field(description="User's first name")
    last_name: str = Field(description="User's last name")


class User(BaseModelNoExtra):
    """User information for financial advice domain."""

    user_id: str = Field(description="Unique identifier for the user")
    name: UserName = Field(description="User's name")
    address: UserAddress = Field(description="User's address")
    email: str = Field(description="User's email address")
    dob: str = Field(description="Date of birth in YYYY-MM-DD format")
    recommended_product: str = Field(
        default="", description="Current product recommendation (empty initially)"
    )


class FinancialAdviceDB(DB):
    """Database interface for financial advice domain."""

    users: Dict[str, User] = Field(
        default_factory=dict, description="All users in the system"
    )
    current_user_id: str = Field(default="", description="The current user ID")

    def get_statistics(self) -> Dict[str, Any]:
        """Get the statistics of the database."""
        total_users = len(self.users)

        return {
            "total_users": total_users,
        }

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get a user by their ID."""
        return self.users.get(user_id)

    def add_user(self, user: User) -> None:
        """Add a new user to the database."""
        self.users[user.user_id] = user

    def update_user_recommendation(self, product_name: str) -> bool:
        """Update the recommended product for a user."""
        if self.current_user_id in self.users:
            self.users[self.current_user_id].recommended_product = product_name
            return True
        return False


def get_db():
    """Get an instance of the telecom database."""
    return FinancialAdviceDB.load(FINANCIAL_ADVICE_DB_PATH)


if __name__ == "__main__":
    db = get_db()
    print(db.get_statistics())
