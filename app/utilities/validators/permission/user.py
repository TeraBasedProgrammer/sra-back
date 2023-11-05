from typing import Optional

from app.models.db.companies import Company, RoleEnum
from app.models.db.users import User


def validate_user_company_role(
    company: Company, user: User, roles: Optional[tuple[RoleEnum]] = None
) -> bool:
    """Validates if user has a specific role(-s) in the company (or any)

    Args:
        company (Company): Company instance
        user (User): User instance
        role (Optional[tuple[RoleEnum]]): RoleEnum tuple. If None, the function skips role validation

    Returns:
        bool: indicates wether user has a specific role in the company or not
    """
    if not roles:
        user = list(filter(lambda x: x.users.id == user.id, company.users))
        if not user:
            return False
    else:
        user = list(
            filter(lambda x: x.users.id == user.id and x.role in roles, company.users)
        )
        if not user:
            return False

    return True
