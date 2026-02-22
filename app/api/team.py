from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.schemas.member import JoinProject, ProjectMemberOut
from app.models.user import User
from app.service.team_service import TeamService

router = APIRouter()

# 1. 通过邀请码加入项目
@router.post("/join", response_model=ProjectMemberOut)
def join_project(
    join_in: JoinProject,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    team_service = TeamService(db)
    return team_service.join_project(join_in, current_user)

# 2. 查看项目成员列表
@router.get("/{project_id}", response_model=List[ProjectMemberOut])
def read_members(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    team_service = TeamService(db)
    return team_service.read_members(project_id, current_user)

# 3. 移除成员 (踢人)
@router.delete("/{project_id}/{user_id}")
def kick_member(
    project_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    team_service = TeamService(db)
    team_service.kick_member(project_id, user_id, current_user)
    return {"msg": "成员已被移除"}

# 4. 退出项目
@router.post("/{project_id}/leave")
def leave_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    team_service = TeamService(db)
    team_service.kick_member(project_id, current_user.id, current_user) # type: ignore
    return {"msg": "你已退出项目"}

# 5. 转让拥有者权限
@router.post("/{project_id}/transfer_owner/{new_owner_id}")
def transfer_owner(
    project_id: int,
    new_owner_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    team_service = TeamService(db)
    team_service.change_owner(project_id, current_user.id, new_owner_id) # type: ignore
    return {"msg": "项目拥有者已转让"}

# 6. 更改成员权限 (admin <-> member)
@router.post("/{project_id}/change_role/{user_id}")
def change_member_permission(
    project_id: int,
    user_id: int,
    new_role: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    team_service = TeamService(db)
    team_service.change_member_role(project_id, user_id, new_role, current_user) # type: ignore
    return {"msg": "成员权限已更改"}