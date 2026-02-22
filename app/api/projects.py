from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.schemas.project import ProjectCreate, ProjectOut
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.service.project_service import ProjectService


router = APIRouter()

# 1. 创建项目接口
@router.post("/", response_model=ProjectOut)
def create_new_project(
    project_in: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # 必须登录
):
    
    project_service = ProjectService(db=db)
    return project_service.create_new_project(project_in=project_in, current_user=current_user)

# 2. 获取我的项目列表接口
@router.get("/", response_model=List[ProjectOut])
def read_my_projects(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # 必须登录
):
    project_service = ProjectService(db=db)
    projects = project_service.read_my_projects(current_user=current_user, skip=skip, limit=limit)
    return projects

# 3. 获取特定项目详情接口
@router.get("/{project_id}", response_model=ProjectOut)
def read_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project_service = ProjectService(db=db)
    project = project_service.read_project(project_id=project_id, current_user=current_user)
    return project  

# 4. 删除项目接口
@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project_endpoint(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project_service = ProjectService(db=db)
    project_service.delete_project(project_id=project_id, current_user=current_user)
    return None