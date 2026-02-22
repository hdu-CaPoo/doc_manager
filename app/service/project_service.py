from sqlalchemy.orm import Session

from app.crud.member import get_member
from app.schemas.project import ProjectCreate
from app.crud.project import create_project, get_user_projects, get_project, delete_project
from app.models.user import User
from app.core.exceptions import ResourceNotFound, PermissionDenied

class ProjectService:
    def __init__(self, db: Session):
        self.db = db

    def create_new_project(
        self,
        project_in: ProjectCreate,
        current_user: User
    ):
        #这里直接调用了curd层的create_project函数，保持了业务逻辑的清晰和分层
        return create_project(db=self.db, project_in=project_in, owner_id=current_user.id) # type: ignore

    def read_my_projects(
        self,
        current_user: User,
        skip: int = 0,
        limit: int = 100
    ):
        projects = get_user_projects(self.db, user_id=current_user.id, skip=skip, limit=limit) # type: ignore
        return projects
    
    def read_project(
        self,
        project_id: int,
        current_user: User
    ):
        # 1. 检查项目是否存在
        project = get_project(self.db, project_id=project_id) # type: ignore
        if not project:
            raise ResourceNotFound("项目不存在")
        
        # 2. 权限检查
        if not get_member(self.db, project_id, current_user.id): # type: ignore
            raise PermissionDenied("你不是该项目成员")
        
        return project
    
    def delete_project(
        self,
        project_id: int,
        current_user: User
    ):
        # 1. 检查项目是否存在
        project = get_project(self.db, project_id) # type: ignore
        if not project:
            raise ResourceNotFound("项目不存在")
        
        # 2. 权限检查 (只有拥有者可以删除)
        member = get_member(self.db, project_id, current_user.id) # type: ignore
        if not member or member.role != "owner": # type: ignore
            raise PermissionDenied("只有项目拥有者可以删除项目")
        
        delete_project(self.db, project_id) # type: ignore