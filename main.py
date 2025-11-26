from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy.orm import Session

import models
from database import engine
import schemas, crud
from auth import (
    get_db, verify_password,
    create_access_token, get_current_user
    
)

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.post("/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    
    if crud.get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email already exists")

    return crud.create_user(db, user)

@app.post("/login", response_model=schemas.Token)
def login(credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, credentials.email)

    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials or no such user")
    
    if not verify_password(credentials.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token({"sub": str(db_user.id)})

    return {"access_token": token, "token_type": "bearer"}

@app.get("/me", response_model=schemas.User)
def get_me(current_user = Depends(get_current_user)):
    return current_user

##
@app.post("/posts", response_model=schemas.Post)
def create_post(post: schemas.PostCreate,current_user = Depends(get_current_user),db: Session = Depends(get_db)):
    return crud.create_post(db, post, user_id=current_user.id)

@app.get("/posts", response_model=list[schemas.Post])
def read_my_posts(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    return crud.get_user_posts(db, user_id=current_user.id)