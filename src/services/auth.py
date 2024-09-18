from typing import Optional
from datetime import datetime, timedelta

from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from src.settings import settings
from src.database.db import get_db
from src.database.models import User
from src.database.repository.users import get_user_by_email


class Auth:
    """
    Class handling authentication-related operations such as password hashing, token generation, and user verification.
    """

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = settings.jwt_secret_key
    ALGORITHM = settings.jwt_algorithm
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login", auto_error=False)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verifies if the plain password matches the hashed password.

        Args:
            plain_password (str): The plain password to be verified.\n
            hashed_password (str): The hashed password to compare against.\n

        Returns:
            bool: True if the plain password matches the hashed password, False otherwise.
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """
        Returns the hashed version of the provided password.

        Args:
            password (str): The password to be hashed.

        Returns:
            str: The hashed password.
        """
        return self.pwd_context.hash(password)

    def create_access_token(
        self, data: dict, expires_delta: Optional[float] = None
    ) -> str:
        """
        Creates an access token for the given data.

        Args:
            data (dict): The data to be encoded in the access token.\n
            expires_delta (float, optional): The expiration time in seconds for the access token. Defaults to None.\n

        Returns:
            str: The encoded access token.
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.now() + timedelta(days=1)
        to_encode.update(
            {
                "iat": datetime.now(),
                "exp": expire,
            }
        )
        encoded_access_token = jwt.encode(
            to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM
        )
        return encoded_access_token

    async def get_current_user(
        self, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
    ) -> User:
        """
        Returns the current user based on the provided access token.

        Args:
            token (str, optional): The access token. Defaults to Depends(oauth2_scheme).\n
            db (Session, optional): The database session. Defaults to Depends(get_db).\n

        Raises:
            HTTPException: If the access token is invalid or expired.

        Returns:
            User: The current user.
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        email = None
        try:
            payload: dict = jwt.decode(
                token, self.SECRET_KEY, algorithms=[self.ALGORITHM]
            )
            email = payload.get("sub")
            if email is None:
                raise credentials_exception
        except (JWTError, AttributeError):
            raise credentials_exception
        user = await get_user_by_email(db, email)
        if user is None:
            raise credentials_exception
        return user

    async def create_reset_password_token(self, email: str, request: Request) -> str:
        """
        Creates a reset password token for the given email.

        Args:
            email (str): The email to be encoded in the token.\n
            request (Request): The request object.

        Returns:
            str: The reset password token.
        """
        expires = timedelta(hours=1)
        return self.create_access_token(
            data={"sub": email, "type": "reset_password"},
            expires_delta=expires.total_seconds(),
        )

    async def decode_reset_password_token(self, token: str) -> dict:
        """
        Decodes the reset password token.

        Args:
            token (str): The reset password token.

        Returns:
            dict: The decoded token.
        """
        try:
            payload: dict = jwt.decode(
                token, self.SECRET_KEY, algorithms=[self.ALGORITHM]
            )
            return payload
        except JWTError:
            return {}


auth_service = Auth()
