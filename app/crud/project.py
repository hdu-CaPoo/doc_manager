import shutil
import uuid
from sqlalchemy.orm import Session
from app.models.project import Project, ProjectMember
from app.schemas.project import ProjectCreate
from app.utils.file_ops import UPLOAD_ROOT 

# 辅助函数：生成唯一的邀请码 (简单版)
def generate_invitation_code():
    return str(uuid.uuid4())[:8] # 取 UUID 的前8位

# 1. 创建项目
def create_project(db: Session, project_in: ProjectCreate, owner_id: int):
    # 生成邀请码
    code = generate_invitation_code()
    # 哪怕只有亿分之一的概率重复，也要处理一下（此处略简，生产环境可以用 while 循环检查）

    # 1. 创建 Project 对象
    db_project = Project(
        name=project_in.name,
        description=project_in.description,
        invitation_code=code,
        owner_id=owner_id
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)

    # 2. 重点：创建者自动成为该项目的管理员/成员
    # 向 project_members 表插入一条记录
    db_member = ProjectMember(
        user_id=owner_id,
        project_id=db_project.id,
        role="owner" # 创建者默认是 owner
    )
    db.add(db_member)
    db.commit()

    return db_project

# 2. 获取某个特定项目
def get_project(db: Session, project_id: int):
    return db.query(Project).filter(Project.id == project_id).first()

# 3. 获取当前用户参与的所有项目
# 这涉及到多对多查询
def get_user_projects(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    # 方法A：直接查 ProjectMember 表，然后关联 Project
    # 方法B：从 User 对象的 relationship 里拿（更 Pythonic，但分页稍麻烦）
    
    # 这里用 SQL 查询方式更直观：
    # "给我找出所有 project_members 表里 user_id 是我的记录，对应的 project"
    return db.query(Project)\
             .join(ProjectMember)\
             .filter(ProjectMember.user_id == user_id)\
             .offset(skip)\
             .limit(limit)\
             .all()

import os
def delete_project(db: Session, project: Project):
    # 1. 删除物理文件
    # 项目文件夹路径通常是 uploads/{project_id}
    project_dir = os.path.join(UPLOAD_ROOT, str(project.id))
    
    if os.path.exists(project_dir):
        try:
            shutil.rmtree(project_dir) # 递归删除文件夹及其内容
            print(f"Deleted project directory: {project_dir}")
        except Exception as e:
            print(f"Error deleting directory {project_dir}: {e}")
            # 这里可以选择是否抛出异常，或者记录日志后继续删除数据库记录

    # 2. 删除数据库记录
    # 如果你的数据库外键设置了 ondelete='CASCADE'，删除 project 会自动删除关联的 members, issues, documents 等
    # 如果没有设置，你需要手动先删除关联表的数据，或者确保 SQLAlchemy 的 relationship 配置了 cascade="all, delete"
    
    db.delete(project)
    db.commit()