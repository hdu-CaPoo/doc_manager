from typing import List
from sqlalchemy.orm import Session

from app.schemas.member import JoinProject, ProjectMemberOut
from app.crud.member import get_project_by_code, get_member, add_member, get_project_members, remove_member, change_owner, change_member_role
from app.crud.project import get_project
from app.models.user import User
from app.core.exceptions import ResourceNotFound, PermissionDenied, BusinessError


class TeamService:
    def __init__(self, db: Session):
        self.db = db

    def join_project(self, join_in: JoinProject, current_user: User):
        # 1. 检查邀请码有效性
        project = get_project_by_code(self.db, join_in.invitation_code)
        if not project:
            raise ResourceNotFound("无效的邀请码")
        
        # 2. 检查是否已经是成员
        if get_member(self.db, project.id, current_user.id): # type: ignore
            raise BusinessError("你已经是该项目成员了")
        
        # 3. 加入
        return add_member(self.db, project.id, current_user.id) # type: ignore
    
    def read_members(self, project_id: int, current_user: User) -> List[ProjectMemberOut]:
        # 1. 检查项目存在
        project = get_project(self.db, project_id)
        if not project:
            raise ResourceNotFound("项目不存在")
        
        # 2. 只有成员才能看成员列表（防止路人偷窥）
        if not get_member(self.db, project_id, current_user.id): # type: ignore
            raise PermissionDenied("你不是该项目成员")
            
        return get_project_members(self.db, project_id) # type: ignore
    
    def kick_member(self, project_id: int, user_id: int, current_user: User):
        # 1. 检查项目存在
        project = get_project(self.db, project_id)
        if not project:
            raise ResourceNotFound("项目不存在")

        # 2. 获取目标成员关系
        target_member = get_member(self.db, project_id, user_id)
        if not target_member:
            raise ResourceNotFound("目标成员不存在")
        
        # 3. 权限检查：只有admin owner能踢人
        current_member = get_member(self.db, project_id, current_user.id) # type: ignore
        if not current_member or current_member.role not in ['admin', 'owner']: # type: ignore
            raise PermissionDenied("只有项目管理员或所有者才能移除成员")
        
        # 4. 不能踢自己
        if user_id == current_user.id:
            raise BusinessError("你不能移除自己")
        
        # 5. 管理员不能相互踢 也不能越权踢
        if target_member.role == "admin" or target_member.user_id == project.owner_id: # type: ignore
            raise PermissionDenied("不能移除其他管理员或项目拥有者")

        # 6. 执行移除
        remove_member(self.db, target_member)

    def leave_project(self, project_id: int, current_user: User):
        # 1. 检查项目存在
        project = get_project(self.db, project_id)
        if not project:
            raise ResourceNotFound("项目不存在")

        # 2. 获取成员关系
        member = get_member(self.db, project_id, current_user.id) # type: ignore
        if not member:
            raise ResourceNotFound("你不是该项目成员")
        
        # 3. 如果是owner，不能直接离开，必须先转移所有权
        if member.role == "owner": # type: ignore
            raise BusinessError("项目拥有者必须先转移所有权才能离开项目")
        
        # 4. 执行离开
        remove_member(self.db, member)

    def transfer_ownership(self, project_id: int, new_owner_id: int, current_user: User):
        # 1. 检查项目存在
        project = get_project(self.db, project_id)
        if not project:
            raise ResourceNotFound("项目不存在")

        # 2. 获取当前成员关系
        current_member = get_member(self.db, project_id, current_user.id) # type: ignore
        if not current_member or current_member.role != "owner": # type: ignore
            raise PermissionDenied("只有项目拥有者才能转移所有权")
        
        # 3. 获取新成员关系
        new_owner_member = get_member(self.db, project_id, new_owner_id)
        if not new_owner_member:
            raise ResourceNotFound("新的项目拥有者必须是项目成员")
        
        # 4. 执行转移
        change_owner(self.db, current_member, new_owner_member)

    def change_member_role(self, project_id: int, user_id: int, new_role: str, current_user: User):
        # 1. 检查项目存在
        project = get_project(self.db, project_id)
        if not project:
            raise ResourceNotFound("项目不存在")

        # 2. 获取当前成员关系
        current_member = get_member(self.db, project_id, current_user.id) # type: ignore
        if not current_member or current_member.role != "owner": # type: ignore
            raise PermissionDenied("只有项目拥有者才能更改成员权限")
        
        # 3. 获取目标成员关系
        target_member = get_member(self.db, project_id, user_id)
        if not target_member:
            raise ResourceNotFound("目标成员不存在")
        
        # 4. 不能修改自己权限
        if user_id == current_user.id:
            raise BusinessError("你不能修改自己的权限")
        
        # 5. 执行修改
        change_member_role(self.db, target_member, new_role)