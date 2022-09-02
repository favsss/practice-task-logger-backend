from datetime import date, datetime, time
from lib2to3.pytree import Base
from typing import List, Union
from pydantic import BaseModel

class UserBase(BaseModel):
    user_name: str 
    email: str 

class UserCreate(UserBase):
    password: str 

class User(UserBase):
    id: int 
    
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str 
    token_type: str 

class TokenData(BaseModel):
    username: Union[str, None] = None

class ProjectBase(BaseModel):
    name: str 

class ProjectCreate(ProjectBase):
    pass

class Project(ProjectBase):
    id: int 

    class Config:
        orm_mode = True 

class TaskBase(BaseModel):
    user_id: int 
    project_id: int 
    start_time: time
    end_time: time
    task_date: date
    duration: int
    description: str

class TaskCreate(BaseModel):
    project_id: int 
    start_time: str
    end_time: str 
    task_date: date
    duration: int
    description: str

class Task(TaskBase):
    id: int 

    class Config:
        orm_mode = True 

    