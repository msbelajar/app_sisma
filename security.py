import datetime
from typing import Optional
from fastapi import HTTPException, Depends, status, Cookie
from random import randint
from schemas import Role
# from passlib.context import CryptContext
import bcrypt
from fastapi.responses import RedirectResponse
from jose import jwt, JWTError
from dotenv import load_dotenv
import os

load_dotenv()

# pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

def rand_password(digit:int=6):
    return str(randint(10**(digit-1), 10**digit - 1))    

def genpass(data: str):
    hashed = bcrypt.hashpw(data.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')
#    return bcrypt.hashpw(data.encode(), bcrypt.gensalt())
#    return pwd.hash(data.encode(), bcrypt.gensalt())

def checkpass(password : str, hashpassword : str) -> bool:
    # return bcrypt.checkpw(password=password.encode(), hashed_password=hashpassword)
    # return bcrypt.checkpw(password.encode('utf-8'), hashpassword.encode('utf-8'))
    if isinstance(hashpassword, str):
        hashpassword = hashpassword.encode('utf-8')  # convert back to bytes
    return bcrypt.checkpw(password.encode('utf-8'), hashpassword)


def verify_token(token:str):
   try:
        payload = jwt.decode(token, key=os.getenv("JWT_SECRET"),algorithms=[os.getenv("JWT_ALGORITHM")])
        return payload
   except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate" : "Bearer"}
        )

def create_access_token(data: dict, expires_delta: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_WEEKS"))):
    to_encode = data.copy()
    #expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=expires_delta)
    expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(weeks=expires_delta)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, os.getenv("JWT_SECRET"), algorithm=os.getenv("JWT_ALGORITHM"))
    return encoded_jwt

def verify_cookie_token(access_token: Optional[str] = Cookie(None)):
    """Dependency to verify access token from cookies"""
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    try:
        payload = jwt.decode(access_token, os.getenv("JWT_SECRET"), algorithms=[os.getenv("JWT_ALGORITHM")])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

# def get_current_user(token:str = Depends(oauth2sch)):
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="invalid"
#     )
#     try:
#         payload = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=[os.getenv("JWT_ALGORITHM")])
#         return UserC(username=payload.get("sub"), name=payload.get("name") ,role=payload.get("role"))
#     except:
#         raise credentials_exception
    
def permission(min_allow:Role):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="not allowed"
    )
    try:
        payload = verify_cookie_token()
        if payload.role > min_allow:
             raise credentials_exception
    except HTTPException:
        raise credentials_exception

# def check_auth_mhs(nim:str, data : UserC):
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="invalid",
#     )
#     try:
#         if data.username == nim or data.role < Role.mahasiswa:
#             return data
#         else:
#             credentials_exception
#     except:
#         raise credentials_exception