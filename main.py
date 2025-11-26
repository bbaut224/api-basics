from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

import models
from database import engine
import schemas, crud
from auth import (
    get_db, verify_password,
    
)

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.post("/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    
    if crud.get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email already exists")

    
    return crud.create_user(db, user)


