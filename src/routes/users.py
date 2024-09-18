from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Request,
)
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.database.repository.users import (
    add_user,
    get_user_by_email,
)
from src.schemas import (
    UserCreate,
    Token,
    UserResponse,
)
from src.services.auth import auth_service


router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate, db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """
    Create a new user.

    Args:
        user (UserCreate): The user data to be created.

    Returns:
        UserResponse: The created user data.
    """
    try:
        user.password = auth_service.get_password_hash(user.password)
        return await add_user(db=db, user=user)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or username already registered.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error: {e}",
        )


@router.post("/login", response_model=Token)
async def login(
    request: Request,
    body: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
) -> Token:
    """
    Login a user.

    Args:
        request (Request): The request object.\n
        user (UserLogin): The user data to be logged in.

    Returns:
        Token: The access token.
    """
    try:
        db_user = await get_user_by_email(db=db, email=body.username)
        if not db_user or not auth_service.verify_password(
            body.password, db_user.password
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password.",
            )
        return {
            "access_token": auth_service.create_access_token({"sub": db_user.email})
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error: {e}",
        )
