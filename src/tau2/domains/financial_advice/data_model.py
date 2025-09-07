"""Data models for the financial advice domain."""

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import Field

from tau2.domains.financial_advice.utils import FINANCIAL_ADVICE_DB_PATH
from tau2.environment.db import DB
from tau2.utils.pydantic_utils import BaseModelNoExtra


class RiskTolerance(str, Enum):
    """Risk tolerance levels for customers."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ProductType(str, Enum):
    """Types of financial products available."""

    SHARE_DEALING_ISA = "Share Dealing ISA"
    SHARE_DEALING_ACCOUNT = "Share Dealing Account"
    READY_MADE_INVESTMENT_ISA = "Ready Made Investment ISA"
    READY_MADE_GENERAL_INVESTMENT_ACCOUNT = "Ready Made General Investment Account"
    FIXED_RATE_CASH_ISA = "Fixed Rate Cash ISA"
    CASH_ISA = "Cash ISA"
    ONLINE_FIXED_BOND = "Online Fixed Bond"
    MONTHLY_SAVER = "Monthly Saver"
    EASY_SAVER = "Easy Saver"


class FinancialProfile(BaseModelNoExtra):
    """Financial profile containing customer preferences and situation."""

    wants_investment_returns: bool = Field(
        description="Whether customer wants higher returns than savings accounts (>6%)"
    )
    has_isa_allowance: bool = Field(
        description="Whether customer has ISA allowance remaining for current tax year"
    )
    wants_own_investments: bool = Field(
        description="Whether customer wants to pick their own investments (vs managed funds)"
    )
    accepts_risk: bool = Field(
        description="Whether customer accepts risk of losing money/putting capital at risk"
    )
    prefers_fixed_rates: bool = Field(
        description="Whether customer prefers fixed interest rates (vs variable)"
    )
    wants_instant_access: bool = Field(
        description="Whether customer wants instant access to savings (vs willing to lock away)"
    )


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
    financial_profile: FinancialProfile = Field(
        description="User's financial profile and preferences"
    )
    expected_recommended_product: str = Field(
        description="Expected product recommendation based on profile"
    )
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

        # Count users by expected product recommendation
        product_counts = {}
        for user in self.users.values():
            product = user.expected_recommended_product
            product_counts[product] = product_counts.get(product, 0) + 1

        # Count users by risk tolerance (derived from financial profile)
        risk_counts = {"low": 0, "medium": 0, "high": 0}
        for user in self.users.values():
            profile = user.financial_profile
            if profile.wants_investment_returns and profile.accepts_risk:
                risk_counts["high"] += 1
            elif not profile.wants_investment_returns and profile.prefers_fixed_rates:
                risk_counts["low"] += 1
            else:
                risk_counts["medium"] += 1

        return {
            "total_users": total_users,
            "product_recommendations": product_counts,
            "risk_tolerance_distribution": risk_counts,
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

    def get_users_by_expected_product(self, product_name: str) -> List[User]:
        """Get all users with a specific expected product recommendation."""
        return [
            user
            for user in self.users.values()
            if user.expected_recommended_product == product_name
        ]

    def get_users_by_risk_tolerance(self, risk_level: RiskTolerance) -> List[User]:
        """Get all users with a specific risk tolerance level."""
        users = []
        for user in self.users.values():
            profile = user.financial_profile
            if risk_level == RiskTolerance.HIGH:
                if profile.wants_investment_returns and profile.accepts_risk:
                    users.append(user)
            elif risk_level == RiskTolerance.LOW:
                if not profile.wants_investment_returns and profile.prefers_fixed_rates:
                    users.append(user)
            else:  # MEDIUM
                if not (
                    profile.wants_investment_returns and profile.accepts_risk
                ) and not (
                    not profile.wants_investment_returns and profile.prefers_fixed_rates
                ):
                    users.append(user)
        return users


def get_db():
    """Get an instance of the telecom database."""
    return FinancialAdviceDB.load(FINANCIAL_ADVICE_DB_PATH)


if __name__ == "__main__":
    db = get_db()
    print(db.get_statistics())
