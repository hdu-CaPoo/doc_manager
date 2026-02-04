from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.member import get_member
from app.schemas.project import ProjectCreate, ProjectOut
from app.crud.project import create_project, get_user_projects, get_project, delete_project
from app.api.deps import get_db, get_current_user
from app.models.user import User

router = APIRouter()

# 1. 创建项目接口
@router.post("/", response_model=ProjectOut)
def create_new_project(
    project_in: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # 必须登录
):
    return create_project(db=db, project_in=project_in, owner_id=current_user.id)

# 2. 获取我的项目列表接口
@router.get("/", response_model=List[ProjectOut])
def read_my_projects(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # 必须登录
):
    projects = get_user_projects(db, user_id=current_user.id, skip=skip, limit=limit)
    return projects

# 3. 获取特定项目详情接口
@router.get("/{project_id}", response_model=ProjectOut)
def read_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = get_project(db, project_id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    #2.权限检查
    if not get_member(db, project_id, current_user.id):
        raise HTTPException(status_code=403, detail="你不是该项目成员")
    
    return project

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project_endpoint(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除项目 (只有拥有者可以操作)
    """
    # 1. 检查项目是否存在
    project = get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    # 2. 权限检查：必须是 Owner
    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=403, 
            detail="权限不足，只有项目拥有者可以删除项目"
        )
    
    # 3. 执行删除
    delete_project(db, project)
    
    # 204 No Content 不需要返回 body
    return