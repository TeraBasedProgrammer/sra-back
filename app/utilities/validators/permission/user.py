from typing import Optional

from app.models.db.companies import RoleEnum
from app.repository.company import CompanyMember


def _get_role_validation_condition(
    member: CompanyMember, roles: tuple[RoleEnum]
) -> bool:
    return True if not roles else member.role in roles


def validate_user_company_role(
    members: list[CompanyMember], user_id: int, roles: Optional[tuple[RoleEnum]] = None
) -> bool:
    """Validates if user has a specific role(-s) in the company (or any)

    Args:
        members (list[CompanyMember]): list of company members data
        user_id (int): current user id
        roles (Optional[tuple[RoleEnum]], optional): tuple of roles for permission validation.
        If None, role validation is skipped. Defaults to None.

    Returns:
        bool: flag that defines wether current user is a member of the company or not
    """

    for member in members:
        if user_id == member.id and _get_role_validation_condition(member, roles):
            return True

    return False
