# coding: utf-8
from sqlalchemy import Column, Date, ForeignKey, Integer, String, Time, text
from sqlalchemy.orm import relationship
from .database import Base

metadata = Base.metadata


class Project(Base):
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True, server_default=text("nextval('projects_id_seq'::regclass)"))
    name = Column(String(255))


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, server_default=text("nextval('users_id_seq'::regclass)"))
    user_name = Column(String(255))
    password = Column(String(255))
    email = Column(String(255))


class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True, server_default=text("nextval('tasks_id_seq'::regclass)"))
    user_id = Column(ForeignKey('users.id'))
    project_id = Column(ForeignKey('projects.id'))
    start_time = Column(Time)
    end_time = Column(Time)
    task_date = Column(Date)
    duration = Column(Integer)
    description = Column(String(255))

    project = relationship('Project')
    user = relationship('User')