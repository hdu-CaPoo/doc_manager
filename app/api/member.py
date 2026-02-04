from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas.member import JoinProject, ProjectMemberOut
from app.crud.member import (
    get_project_by_code,
    get_member,
    add_member,
    get_project_members,
    remove_member,
    change_owner,
    change_member_role,
)
from app.crud.project import get_project
from app.api.deps import get_db, get_current_user
from app.models.user import User

router = APIRouter()


# 1. 通过邀请码加入项目
@router.post("/join", response_model=ProjectMemberOut)
def join_project(
    join_in: JoinProject,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # a. 检查邀请码有效性
    project = get_project_by_code(db, join_in.invitation_code)
    if not project:
        raise HTTPException(status_code=404, detail="无效的邀请码")

    # b. 检查是否已经是成员
    if get_member(db, project.id, current_user.id):
        raise HTTPException(status_code=400, detail="你已经是该项目成员了")

    # c. 加入
    return add_member(db, project.id, current_user.id)


# 2. 查看项目成员列表
@router.get("/{project_id}", response_model=List[ProjectMemberOut])
def read_members(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # a. 检查项目存在
    project = get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    # b. 只有成员才能看成员列表（防止路人偷窥）
    if not get_member(db, project_id, current_user.id):
        raise HTTPException(status_code=403, detail="你不是该项目成员")

    return get_project_members(db, project_id)


# 3. 移除成员 (踢人)
@router.delete("/{project_id}/{user_id}")
def kick_member(
    project_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # a. 获取目标成员关系
    target_member = get_member(db, project_id, user_id)
    if not target_member:
        raise HTTPException(status_code=404, detail="该用户不在项目中")

    # b. 权限检查：只有admin owner能踢人
    # 先查出当前的 Member 身份，或者直接用 project.owner_id 对比
    project = get_project(db, project_id)

    # 规则：只有 Project Owner 和admin 才有权踢人
    if not (
        project.owner_id == current_user.id
        or get_member(db, project_id, current_user.id).role == "admin"
    ):
        raise HTTPException(status_code=403, detail="只有项目管理员可以移除成员")

    # c. 不能踢自己 (防止项目变成没管理员的孤儿)
    if user_id == current_user.id:
        raise HTTPException(
            status_code=400, detail="不能移除你自己，请使用退出项目功能"
        )

    # d. 管理员不能相互踢 也不能越权踢
    if target_member.role == "admin" or target_member.user_id == project.owner_id:
        raise HTTPException(status_code=403, detail="不能移除其他管理员或项目拥有者")

    remove_member(db, target_member)
    return {"msg": "成员已移除"}


# 4. 退出项目
@router.post("/{project_id}/leave")
def leave_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 1. 获取当前用户的成员关系
    member = get_member(db, project_id, current_user.id)
    if not member:
        raise HTTPException(status_code=404, detail="你不在该项目中")

    # 2. 如果是项目拥有者，禁止直接退出（防止项目变成没拥有者的孤儿）
    project = get_project(db, project_id)
    if project.owner_id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="项目拥有者不能直接退出项目，请先转让拥有者权限或删除项目",
        )

    remove_member(db, member)
    return {"msg": "你已退出该项目"}


# 5. 转让拥有者权限
@router.post("/{project_id}/transfer_owner/{new_owner_id}")
def transfer_owner(
    project_id: int,
    new_owner_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 1. 检查项目存在
    project = get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    # 2. 检查当前用户是否是拥有者
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="只有项目拥有者可以转让拥有者权限")

    # 3. 检查新拥有者是成员
    new_owner_member = get_member(db, project_id, new_owner_id)
    if not new_owner_member:
        raise HTTPException(status_code=404, detail="新拥有者必须是项目成员")

    # 4. 转让拥有者权限
    change_owner(db, get_member(db, project_id, current_user.id), new_owner_member)
    return {"msg": "拥有者权限已转让"}


# 6. 更改成员权限 (admin <-> member)
@router.post("/{project_id}/change_role/{user_id}")
def change_member_permission(
    project_id: int,
    user_id: int,
    new_role: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 1. 检查项目存在
    project = get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    # 2. 检查当前用户是否是拥有者
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="只有项目拥有者可以更改成员权限")

    # 3. 检查目标成员存在
    target_member = get_member(db, project_id, user_id)
    if not target_member:
        raise HTTPException(status_code=404, detail="该用户不在项目中")

    # 4. 不能更改拥有者权限
    if target_member.user_id == project.owner_id:
        raise HTTPException(status_code=400, detail="不能更改项目拥有者的权限")

    # 5. 更改权限
    if new_role not in ["admin", "member"]:
        raise HTTPException(status_code=400, detail="无效的角色类型")

    change_member_role(db, target_member, new_role)
    return {"msg": "成员权限已更改"}
