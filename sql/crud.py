from sqlalchemy.orm import Session 
from . import models, schemas 
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_users(db: Session):
    return db.query(models.User).all()

def get_user_by_username(db: Session, user_name):
    return db.query(models.User).filter(models.User.user_name == user_name).first()

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(
        user_name=user.user_name,
        password = get_password_hash(user.password),
        email=user.email
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user: schemas.User):
    db.query(models.User).filter(models.User.id == user_id).update(user.dict())
    db.commit()
    db_user = get_user(db, user_id)
    return db_user

def delete_user(db: Session, user_id: int):
    db.query(models.User).filter(models.User.id == user_id).delete()
    db.commit()
    return { "success" : True }

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate_user(db: Session, user_name: str, password: str):
    user = get_user_by_username(db, user_name)
    if not user:
        return False 
    if not verify_password(password, user.password):
        return False 

    return user 

def get_project(db: Session, project_id: int):
    return db.query(models.Project).filter(models.Project.id == project_id).first()

def get_project_by_title(db: Session, name: str):
    return db.query(models.Project).filter(models.Project.name == name).first()

def get_projects(db: Session):
    return db.query(models.Project).all()

def create_project(db: Session, project: schemas.ProjectCreate):
    db_project = models.Project(
        name=project.name
    )

    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

def delete_project(db: Session, project_id: int):
    db.query(models.Project).filter(models.Project.id == project_id).delete()
    db.commit()
    return { "success" : True }

def update_project(db: Session, project_id: int, project: schemas.Project):
    db.query(models.Project).filter(models.Project.id == project_id).update(project.dict())
    db.commit()
    db_project = get_project(db, project_id)
    return db_project

def get_task(db: Session, task_id: int):
    return db.query(models.Task).filter(models.Task.id == task_id).first() 

def get_tasks_by_user(db: Session, user_id: int):
    query = db.query(models.Task, models.Project).filter(models.Task.project_id == models.Project.id).filter(models.Task.user_id == user_id).all()
    tasks = []
    for t, p in query:
        tasks.append({
            'id' : t.id,
            'user_id' : t.user_id, 
            'project_id' : t.project_id,
            'start_time' : t.start_time,
            'end_time' : t.end_time,
            'task_date' : t.task_date,
            'description' : t.description,
            'duration' : t.duration,
            'project_name' : p.name
        })

    return tasks

def get_tasks_by_project(db: Session, project_id: int):
    return db.query(models.Task).filter(models.Task.project_id == project_id).all()

def create_task(db: Session, task: schemas.TaskCreate, user_id: int):
    print("FAVS")
    db_task = models.Task(
        user_id=user_id,
        project_id=task.project_id,
        start_time=task.start_time,
        end_time=task.end_time,
        task_date=task.task_date,
        duration=task.duration,
        description=task.description
    )

    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    db_project = db.query(models.Project).filter(models.Project.id == db_task.project_id).first()

    return {
        "id" : db_task.id,
        "user_id" : db_task.user_id,
        "project_id" : db_task.project_id,
        "start_time" : db_task.start_time,
        "end_time" : db_task.end_time,
        "task_date" : db_task.task_date,
        "duration" : db_task.duration,
        "description" : db_task.duration,
        "project_name" : db_project.__dict__["name"]
    }

def delete_task(db: Session, task_id: int):
    db.query(models.Task).filter(models.Task.id == task_id).delete()
    db.commit()
    return { "success" : True }

def delete_task_by_user_id(db: Session, user_id: int):
    db.query(models.Task).filter(models.Task.user_id == user_id).delete()
    db.commit()

def delete_task_by_project_id(db: Session, project_id: int):
    db.query(models.Task).filter(models.Task.project_id == project_id).delete()
    db.commit() 

def update_task(db: Session, task_id: int, task: schemas.Task):
    db.query(models.Task).filter(models.Task.id == task_id).update(task.dict())
    db.commit()
    db_task = get_task(db, task_id)

    db_project = get_project(db, db_task.__dict__["project_id"])

    return {
        "id" : task.id,
        "user_id" : task.user_id,
        "project_id" : task.project_id,
        "start_time" : task.start_time,
        "end_time" : task.end_time,
        "task_date" : task.task_date,
        "duration" : task.duration,
        "description" : task.description,
        "project_name" : db_project.__dict__["name"]
    } 



