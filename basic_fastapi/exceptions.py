from fastapi import HTTPException, status

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"}
)

user_conflict_exception = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="user name already exists"
)
