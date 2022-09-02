from tokenize import Token
from fastapi import FastAPI, Depends, status, Form, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from sql import crud, models, schemas
from sql.database import SessionLocal, engine

from datetime import datetime, timedelta
from jose import JWTError, jwt
from typing import Optional, List
from sqlalchemy.orm.session import Session

from fastapi.middleware.cors import CORSMiddleware

SECRET_KEY = "327b399999b80ff736dc6e5285918902fc1f6cbe290ecd869910f0054558a071"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

origins = [
    "http://localhost:8080"
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes = 15)
    
    to_encode.update({ "exp" : expire })
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm = ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate" : "Bearer"}
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        print("username is {}".format(username))
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception

    print(token_data)
    db = next(get_db())
    user = crud.get_user_by_username(db, token_data.username)
    print(user)
    if user is None:
        raise credentials_exception
    return user

@app.get("/")
async def root():
    return { "message" : "Hello World" }

@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate" : "Bearer"}
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={ "sub" : user.user_name },
        expires_delta=access_token_expires
    )

    return { 
        "access_token" : access_token, 
        "token_type" : "bearer", 
        "user" : { "username" : user.user_name, "email" : user.email } 
    }

@app.get("/users", response_model=List[schemas.User])
def get_users(db: Session = Depends(get_db)):
    return crud.get_users(db)

@app.get("/users/{user_id}", response_model=schemas.User)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = crud.get_user(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/users", response_model=schemas.User)
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, user.user_name)
    if db_user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    return crud.create_user(db, user)

@app.patch("/users/{user_id}", response_model=schemas.User)
def update_user(user_id: int, user: schemas.UserBase, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=400, detail="User not found")
    model_user = schemas.User(**db_user.__dict__)
    updated_data = user.dict(exclude_unset=True)
    updated_user = model_user.copy(update=updated_data)
    return crud.update_user(db, user_id, updated_user)

@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=400, detail="User does not exist")
    crud.delete_task_by_user_id(db, user_id)
    crud.delete_user(db, user_id)

@app.get("/users/me/", response_model=schemas.User)
async def read_users_me(current_user: schemas.User = Depends(get_current_user)):
    return current_user

@app.get("/projects", response_model=List[schemas.Project])
def get_projects(db: Session = Depends(get_db)):
    return crud.get_projects(db)

@app.get("/projects/{project_id}", response_model=schemas.Project)
def get_project(project_id: int, db: Session = Depends(get_db)):
    db_project = crud.get_project(db, project_id)
    if db_project is None:
        raise HTTPException(status_code=400, detail="Project does not exist")

    return db_project 

@app.post("/projects", response_model=schemas.Project)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    db_project = crud.get_project_by_title(db, project.name)
    if db_project:
        raise HTTPException(status_code=400, detail="Project already exists")
    return crud.create_project(db, project)

@app.patch("/projects/{project_id}", response_model=schemas.Project)
def update_project(project_id: int, project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    db_project = crud.get_project(db, project_id)
    if db_project is None:
        raise HTTPException(status_code=400, detail="Project does not exist")

    model_project = schemas.Project(**db_project.__dict__)
    updated_data = project.dict(exclude_unset=True)
    updated_project = model_project.copy(update=updated_data)

    return crud.update_project(db, project_id, updated_project)

@app.delete("/projects/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    db_project = crud.get_project(db, project_id)
    if db_project is None:
        raise HTTPException(status_code=400, detail="Project does not exist")
    crud.delete_task_by_project_id(db, project_id)
    crud.delete_project(db, project_id)
    return { "success" : True }

@app.get("/tasks")
def get_tasks(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    db_tasks = crud.get_tasks_by_user(db, current_user.id)
    return db_tasks

@app.post("/tasks")
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return crud.create_task(db, task, current_user.id)

@app.patch("/tasks/{task_id}")
def update_task(task_id: int, task: schemas.TaskCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    print(task)
    db_task = crud.get_task(db, task_id)
    if db_task is None:
        raise HTTPException(status_code=400, detail="Task logged does not exist")
    updated_task = schemas.Task(
        id=db_task.id,
        user_id=current_user.id,
        project_id=task.project_id,
        start_time=task.start_time,
        end_time=task.end_time,
        task_date=task.task_date,
        duration=task.duration,
        description=task.description
    )

    return crud.update_task(db, task_id, updated_task)

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    db_task = crud.get_task(db, task_id)
    if db_task is None:
        raise HTTPException(status_code=400, detail="Task logged does not exist")
    
    return crud.delete_task(db, task_id)




