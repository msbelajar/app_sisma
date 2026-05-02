import datetime
from typing import Optional
from fastapi import HTTPException, Depends, Request, status, Cookie
from random import randint
from schemas import Role
import bcrypt
from jose import jwt, JWTError
from dotenv import load_dotenv
import os

load_dotenv()

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

def user_cookies(request : Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    try:
        payload = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=[os.getenv("JWT_ALGORITHM")])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    
def permission(min_allow:Role = Role.admin, data = Depends(user_cookies)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="not allowed - insufficient permissions"
    )
    try:
        print(f"User role: {data.get('role')}, Required role: {min_allow}")
        # Only allow if user's role is <= min_allow (lower number = higher privilege)
        if data.get("role") > min_allow:
             raise credentials_exception
    except HTTPException:
        raise credentials_exception

def require_permission(min_allow: Role):
    def permission_check(data = Depends(user_cookies)):
        credentials_exception = HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="not allowed - insufficient permissions"
        )
        try:
            # print(f"User role: {data.get('role')}, Required role: {min_allow}")
            if data.get("role") > min_allow:
                raise credentials_exception
        except HTTPException:
            raise credentials_exception
    return permission_check