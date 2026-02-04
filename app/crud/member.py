from sqlalchemy.orm import Session
from app.models.project import Project, ProjectMember


# 1. 根据邀请码找项目
def get_project_by_code(db: Session, code: str):
    return db.query(Project).filter(Project.invitation_code == code).first()


# 2. 检查用户是否已经在项目里
def get_member(db: Session, project_id: int, user_id: int):
    return (
        db.query(ProjectMember)
        .filter(
            ProjectMember.project_id == project_id, ProjectMember.user_id == user_id
        )
        .first()
    )


# 3. 添加成员
def add_member(db: Session, project_id: int, user_id: int, role: str = "member"):
    db_member = ProjectMember(project_id=project_id, user_id=user_id, role=role)
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member


# 4. 获取项目的所有成员
def get_project_members(db: Session, project_id: int):
    # 这里利用 relationship 直接加载 user 信息
    return db.query(ProjectMember).filter(ProjectMember.project_id == project_id).all()


# 5. 移除成员
def remove_member(db: Session, db_member: ProjectMember):
    db.delete(db_member)
    db.commit()


# 6. 更改用户权限（项目管理员/普通用户）
def change_member_role(db: Session, db_member: ProjectMember, new_role: str):
    db_member.role = new_role
    db.commit()
    db.refresh(db_member)
    return db_member


# 7. 变更拥有者
def change_owner(db: Session, origional_owner: ProjectMember, new_owner: ProjectMember):
    origional_owner.role = "member"
    new_owner.role = "owner"  # 如果你确定要用 "owner" 这个字符串

    # 2. 修改 Project 表的 owner_id
    # 注意：我们要改的是 origional_owner 关联的那个 project 对象
    # 前提是 ProjectMember 模型里有 `project = relationship(...)`
    origional_owner.project.owner_id = new_owner.user_id

    # 3. 提交
    # 不需要 db.add(project)，因为 project 已经通过 relationship 被 session 管理了
    db.add(origional_owner)
    db.add(new_owner)
    db.commit()

    return origional_owner, new_owner
