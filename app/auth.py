from fastapi import Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials

security = HTTPBasic()

USERNAME = "admin"
PASSWORD = "admin123"


def authenticate(
    credentials: HTTPBasicCredentials = Depends(security)
):
    if (
        credentials.username != USERNAME
        or credentials.password != PASSWORD
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    return credentials.username