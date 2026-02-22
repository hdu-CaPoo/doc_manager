from typing import List
from fastapi import BackgroundTasks
from sqlalchemy.orm import Session

from app.crud.issue import create_comment, get_comments_by_issue, create_issue, get_issues_by_project, get_issue_by_id, update_issue, delete_issue # 导入 CRUD
from app.crud.member import get_member
from app.crud.project import get_project
from app.core.email import send_notification_email
from app.core.exceptions import ResourceNotFound, PermissionDenied
from app.schemas.issue import  CommentCreate
from app.models.issue import Issue
from app.models.user import User


class IssueService:
    def __init__(self, db: Session):
        self.db = db

    def create_new_issue(
        self,
        project_id: int,
        title: str,
        content: str,
        priority: str,
        current_user: User
    ) -> Issue:
        # 1. 检查项目是否存在
        project = get_project(self.db, project_id)
        if not project:
            raise ResourceNotFound("项目不存在")
        
        # 2. 检查用户是否为项目成员
        member = get_member(self.db, project_id, current_user.id) #type: ignore
        if not member:
            raise PermissionDenied("你不是该项目成员")
        
        # 3. 创建提问
        new_issue = create_issue(
            self.db,
            project_id=project_id,
            creator_id=current_user.id, #type: ignore
            title=title,
            content=content,
            priority=priority
        )
        return new_issue

    def read_issues_by_project(
        self,
        project_id: int,
        status: str,
        current_user: User
    ) -> List[Issue]:
        # 1. 检查项目是否存在
        project = get_project(self.db, project_id)
        if not project:
            raise ResourceNotFound("项目不存在")
        
        # 2. 检查用户是否为项目成员
        member = get_member(self.db, project_id, current_user.id) #type: ignore
        if not member:
            raise PermissionDenied("你不是该项目成员")
        
        # 3. 获取提问列表
        issues = get_issues_by_project(self.db, project_id=project_id, status=status)
        return issues
    
    def update_existing_issue(
        self,
        project_id: int,
        issue_id: int,
        background_tasks: BackgroundTasks,
        new_status: str,
        new_content: str,
        current_user: User
    ) -> Issue:
        # 1. 检查项目是否存在
        project = get_project(self.db, project_id)
        if not project:
            raise ResourceNotFound("项目不存在")
        
        # 2. 获取提问
        issue = get_issue_by_id(self.db, issue_id)
        if not issue or issue.project_id != project_id: #type: ignore
            raise ResourceNotFound("提问不存在")
        
        # 3. 检查用户是否为项目管理员或拥有者或提问者本人
        member = get_member(self.db, project_id, current_user.id) #type: ignore
        if not member or (member.role not in ["admin", "owner"] and issue.creator_id != current_user.id): #type: ignore
            raise PermissionDenied("你不是该项目管理员或拥有者/该issue提问者，无法更新提问")
        
        # 4. 更新提问
        updated_issue = update_issue(
            db=self.db,
            db_issue=issue, #type: ignore
            new_content=new_content,
            new_status=new_status
        )
        if new_status and new_status != issue.status:
            creator_email = issue.creator.email
            
            background_tasks.add_task(
                send_notification_email, 
                creator_email, 
                f"问题状态更新: [{issue.title}]", 
                "状态变更", 
                f"你的问题状态已更新为: {updated_issue.status}", 
                f"http://doc.capoo.me/issues/{issue_id}"
            )

        return updated_issue
    
    def delete_issue(
        self,
        project_id: int,
        issue_id: int,
        current_user: User
    ):
        # 1. 检查项目是否存在
        project = get_project(self.db, project_id)
        if not project:
            raise ResourceNotFound("项目不存在")
        
        # 2. 获取提问
        issue = get_issue_by_id(self.db, issue_id)
        if not issue or issue.project_id != project_id: #type: ignore
            raise ResourceNotFound("提问不存在")
        
        # 3. 检查用户是否为项目管理员或拥有者或提问者本人
        member = get_member(self.db, project_id, current_user.id) #type: ignore
        if not member or (member.role not in ["admin", "owner"] and issue.creator_id != current_user.id): #type: ignore
            raise PermissionDenied("你不是该项目管理员或拥有者/该issue提问者，无法删除提问")
        

        # 4. 删除提问
        delete_issue(self.db, issue)

    def get_single_issue(
        self,
        project_id: int,
        issue_id: int,
        current_user: User
    ) -> Issue:
        # 1. 检查项目是否存在
        project = get_project(self.db, project_id)
        if not project:
            raise ResourceNotFound("项目不存在")
        
        # 2. 检查用户是否为项目成员
        member = get_member(self.db, project_id, current_user.id) #type: ignore
        if not member:
            raise PermissionDenied("你不是该项目成员")
        
        # 3. 获取提问
        issue = get_issue_by_id(self.db, issue_id)
        if not issue or issue.project_id != project_id: #type: ignore
            raise ResourceNotFound("提问不存在")
        
        return issue
    
    def reply_to_issue(
        self,
        project_id: int,
        issue_id: int,
        comment_in: CommentCreate, # 这里建议用 JSON Body
        background_tasks: BackgroundTasks,
        current_user: User
    ):
        # 1. 检查项目是否存在
        project = get_project(self.db, project_id)
        if not project:
            raise ResourceNotFound("项目不存在")
        
        # 2. 检查用户是否为项目成员
        member = get_member(self.db, project_id, current_user.id) #type: ignore
        if not member:
            raise PermissionDenied("你不是该项目成员")
        
        # 3. 获取提问
        issue = get_issue_by_id(self.db, issue_id)
        if not issue or issue.project_id != project_id: #type: ignore
            raise ResourceNotFound("提问不存在")
        
        # 4. 发送通知邮件 (后台任务)
        # --- 邮件通知逻辑 ---
        # 1. 只有当回复人不是提问者本人时，才发邮件
        if current_user.id != issue.creator_id: #type: ignore
            # 获取提问者的邮箱
            # 这里需要保证 issue.creator 已经加载了，或者重新查一遍 user
            creator_email = issue.creator.email 
            
            email_subject = f"你的问题 [{issue.title}] 有新回复"
            email_content = f"{current_user.nickname} 回复了你：{comment_in.content[:50]}..."
            link = f"http://doc.capoo.me/issues/{issue_id}" # 前端地址

            background_tasks.add_task(
                send_notification_email, 
                creator_email, 
                email_subject, 
                "你有新回复", 
                email_content, 
                link
            )

        # 5. 创建回复
        comment = create_comment(
            db=self.db,
            issue_id=issue_id,
            user_id=current_user.id, #type: ignore
            content=comment_in.content
        )
        return comment
    
    def get_comments_for_issue(
        self,
        project_id: int,
        issue_id: int,
        current_user: User
    ):
        # 1. 检查项目是否存在
        project = get_project(self.db, project_id)
        if not project:
            raise ResourceNotFound("项目不存在")
        
        # 2. 检查用户是否为项目成员
        member = get_member(self.db, project_id, current_user.id) #type: ignore
        if not member:
            raise PermissionDenied("你不是该项目成员")
        
        # 3. 获取提问
        issue = get_issue_by_id(self.db, issue_id)
        if not issue or issue.project_id != project_id: #type: ignore
            raise ResourceNotFound("提问不存在")
        
        # 4. 获取评论列表
        comments = get_comments_by_issue(self.db, issue_id)
        return comments