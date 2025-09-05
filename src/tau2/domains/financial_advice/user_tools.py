"""User tools for the financial advice domain."""

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

    @is_tool(ToolType.READ)
    def get_financial_situation_information(self, user_id: str) -> str:
        """
        Get the user's financial situtation information including their preferences and situation.
        This includes information about their risk tolerance, ISA allowance,
        investment preferences, and other criteria used for product recommendations.

        Args:
            user_id: The user ID to get the financial profile for.

        Returns:
            A formatted string containing the user's financial profile information.
        """
        user = self._get_user(user_id)
        financial_profile = user.financial_profile

        # Format the financial profile information
        profile_info = []
        profile_info.append(
            f"Financial Profile for {user.name.first_name} {user.name.last_name}:"
        )
        profile_info.append("")

        # Investment vs Savings preference
        if financial_profile.wants_investment_returns:
            profile_info.append(
                "• Investment Goals: Wants higher returns than savings accounts (>6%)"
            )
        else:
            profile_info.append("• Investment Goals: Wants savings-level returns (≤6%)")

        # ISA allowance status
        if financial_profile.has_isa_allowance:
            profile_info.append(
                "• ISA Status: Has ISA allowance remaining for current tax year"
            )
        else:
            profile_info.append(
                "• ISA Status: No ISA allowance remaining (already has ISA and no allowance left)"
            )

        # Investment management preference (only relevant for investment products)
        if financial_profile.wants_investment_returns:
            if financial_profile.wants_own_investments:
                profile_info.append(
                    "• Investment Management: Wants to pick own investments"
                )
            else:
                profile_info.append("• Investment Management: Prefers managed funds")

        # Risk acceptance (only relevant for investment products)
        if financial_profile.wants_investment_returns:
            if financial_profile.accepts_risk:
                profile_info.append(
                    "• Risk Tolerance: Accepts risk of losing money/putting capital at risk"
                )
            else:
                profile_info.append(
                    "• Risk Tolerance: Does not accept risk of losing money"
                )

        # Interest rate preference (only relevant for savings products)
        if not financial_profile.wants_investment_returns:
            if financial_profile.prefers_fixed_rates:
                profile_info.append(
                    "• Interest Rate Preference: Prefers fixed interest rates"
                )
            else:
                profile_info.append(
                    "• Interest Rate Preference: Open to variable interest rates"
                )

        # Access preference (only relevant for savings products)
        if not financial_profile.wants_investment_returns:
            if financial_profile.wants_instant_access:
                profile_info.append(
                    "• Access Preference: Wants instant access to savings"
                )
            else:
                profile_info.append("• Access Preference: Willing to lock money away")

        return "\n".join(profile_info)

    @is_tool(ToolType.READ)
    def get_user_basic_info(self, user_id: str) -> str:
        """
        Get basic user information including name, address, and contact details.

        Args:
            user_id: The user ID to get basic information for.

        Returns:
            A formatted string containing the user's basic information.
        """
        user = self._get_user(user_id)

        info = []
        info.append(f"User Information for {user_id}:")
        info.append("")
        info.append(f"Name: {user.name.first_name} {user.name.last_name}")
        info.append(f"Email: {user.email}")
        info.append(f"Date of Birth: {user.dob}")
        info.append("")
        info.append("Address:")
        info.append(f"  {user.address.address1}")
        if user.address.address2:
            info.append(f"  {user.address.address2}")
        info.append(f"  {user.address.city}")
        info.append(f"  {user.address.postcode}")
        info.append(f"  {user.address.country}")

        return "\n".join(info)

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
