from fastapi import APIRouter, HTTPException, Depends, status, Security, BackgroundTasks, Request
from fastapi.security import HTTPBearer, OAuth2PasswordRequestForm, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.repository import auth as repository_auth, users as repository_users
from src.services.auth import auth_service
from src.schemas import UserModel, UserResponse, TokenModel, RequestEmail, RequestPassword
from src.services.email import send_email, reset_password_user

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: UserModel, background_tasks: BackgroundTasks, request: Request, db: Session = Depends(get_db)):
    exist_user = await repository_auth.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists!")
    body.password = auth_service.get_password_hash(body.password)
    user = await repository_auth.create_user(body, db)
    background_tasks.add_task(send_email, user.email, user.username, str(request.base_url))
    return user


@router.post("/login", response_model=TokenModel)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = await repository_auth.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email is not confirmed")
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repository_auth.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get("/refresh_token", response_model=TokenModel)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repository_auth.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repository_auth.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await repository_auth.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    email = auth_service.get_email_from_token(token)
    user = await repository_auth.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.confirmed:
        return {"message": "Your email is already confirmed!"}
    await repository_users.confirmed_email(email, db)
    return {"message": "Email confirmed"}


@router.post("/request_email")
async def request_email(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                        db: Session = Depends(get_db)):
    user = await repository_auth.get_user_by_email(body.email, db)

    if user:
        if user.confirmed:
            return {"message": "Your email is already confirmed"}
        background_tasks.add_task(
            send_email, user.email, user.username, str(request.base_url))
    return {"message": "Check your email for confirmation."}


@router.post("/reset_password")
async def reset_password(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                         db: Session = Depends(get_db)):
    user = await repository_auth.get_user_by_email(body.email, db)

    if user:
        background_tasks.add_task(reset_password_user, user.email, user.username,
                                  str(request.base_url))
    return {"message": "Check your email for confirmation."}


@router.post("/reset/{token}")
async def reset(token: str, password: RequestPassword, db: Session = Depends(get_db)):
    email = auth_service.get_email_from_reset_token(token)
    user = repository_auth.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Reset password error")
    hash_password = auth_service.get_password_hash(password.password)
    await repository_users.update_password(email, hash_password, db)
    return {"message": "You update your password!"}
