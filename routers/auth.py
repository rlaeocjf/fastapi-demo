from fastapi import Depends, HTTPException, APIRouter
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import BaseModel
from typing import Optional

from starlette import status

from passlib.context import CryptContext

from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import jwt, JWTError

import models
from database import engine, SessionLocal, get_db

SECRET_KEY = "hWRhwA4ym01XvkoY"
ALGORITHM = "HS256"


class CreateUser(BaseModel):
    username: str
    email: Optional[str]
    first_name: str
    last_name: str
    password: str
    phone_number: Optional[str]


bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

models.Base.metadata.create_all(bind=engine)

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="token")

router = APIRouter(
    prefix="/auth",
    tags=["권한"],
    responses={401: {"user": "Not authorized"}}
)


# 암호화 된 사용자 패스워드를 돌려 준다
def get_password_hash(password):
    return bcrypt_context.hash(password)


# 패스워드 일치여부 검증
def verify_password(plain_password, hashed_password):
    return bcrypt_context.verify(plain_password, hashed_password)


# 사용자(frontend)로 부터 입력된 plain password와 database에 저장된 hashed password를 비교하여 올바른 password 여부를 돌려준다.
def authenticate_user(username: str, password: str, db: Session = Depends(get_db)):
    user = db.query(models.Users).filter(models.Users.username == username).first()

    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False

    return user


@router.post("/create/user")
async def create_new_user(create_user: CreateUser, db: Session = Depends(get_db)):
    create_user_model = models.Users()
    create_user_model.email = create_user.email
    create_user_model.username = create_user.username
    create_user_model.first_name = create_user.first_name
    create_user_model.last_name = create_user.last_name
    create_user_model.hashed_password = get_password_hash(create_user.password)
    create_user_model.phone_number = create_user.phone_number
    create_user_model.is_active = True

    db.add(create_user_model)
    db.commit()


# jwt를 생성한다 만료시간은 기본 15분
def create_access_token(username: str, user_id: int, expire_delta: Optional[timedelta] = None):
    encode = {"sub": username, "id": user_id}
    if expire_delta:
        expire = datetime.utcnow() + expire_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    encode.update({"exp": expire})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: str = Depends(oauth2_bearer)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        if username is None or user_id is None:
            raise get_user_exception()
        return {"username": username, "user_id": user_id}
    except JWTError:
        raise get_user_exception()


# 로그인 시도한 사용자를 검증하여 jwt를 돌려준다
@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(),
                                 db: Session = Depends(get_db)):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise token_exception()
    token_expires = timedelta(minutes=20)
    token = create_access_token(user.username, user.id, expire_delta=token_expires)

    return {"token": token}


# Exception
def get_user_exception():
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    return credentials_exception


def token_exception():
    token_exception_response = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return token_exception_response
