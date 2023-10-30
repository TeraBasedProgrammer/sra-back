import re

from fastapi import HTTPException, status


def validate_password(value: str):
        if not re.compile(r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$").match(value):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password should contain at least eight characters, at least one letter and one number",
            )
        return value