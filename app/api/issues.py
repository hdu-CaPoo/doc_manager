from typing import List, Optional
from fastapi import APIRouter, BackgroundTasks, Depends, Form
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.schemas.issue import IssueOut, CommentOut, CommentCreate
from app.models.user import User
from app.service.issue_service import IssueService

router = APIRouter()

# 1. 创建新提问
@router.post("/projects/{project_id}/issue/create", response_model=IssueOut)
def create_new_issue(
    project_id: int,
    title: str = Form(...),
    content: str = Form(...),
    priority: str = Form("low"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    issue_service = IssueService(db)
    new_issue = issue_service.create_new_issue(
        project_id=project_id,
        title=title,
        content=content,
        priority=priority,
        current_user=current_user
    )
    return new_issue

# 2. 获取项目的所有提问
@router.get("/projects/{project_id}/issues", response_model=List[IssueOut])
def read_issues_by_project(
    project_id: int,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    issue_service = IssueService(db)
    issues = issue_service.read_issues_by_project(
        project_id=project_id,
        status=status, #type: ignore
        current_user=current_user
    )
    return issues

# 3. 更新提问状态或内容
@router.put("/projects/{project_id}/issues/{issue_id}/update", response_model=IssueOut)
def update_existing_issue(
    project_id: int,
    issue_id: int,
    background_tasks: BackgroundTasks,
    new_status: str = Form(None),
    new_content: str = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    issue_service = IssueService(db)
    updated_issue = issue_service.update_existing_issue(
        project_id=project_id,
        issue_id=issue_id,
        new_status=new_status,
        new_content=new_content,
        current_user=current_user,
        background_tasks=background_tasks
    )
    return updated_issue

# 4. 删除提问
@router.delete("/projects/{project_id}/issues/{issue_id}/delete")
def delete_issue_endpoint(
    project_id: int,
    issue_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    issue_service = IssueService(db)
    issue_service.delete_issue(
        project_id=project_id,
        issue_id=issue_id,
        current_user=current_user
    )
    return {"msg": "提问已删除"}

# 5. 获取单个提问
@router.get("/projects/{project_id}/issues/{issue_id}", response_model=IssueOut)
def read_single_issue(
    project_id: int,
    issue_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    issue_service = IssueService(db)
    issue = issue_service.get_single_issue(
        project_id=project_id,
        issue_id=issue_id,
        current_user=current_user
    )
    return issue

# 6. 回复提问
@router.post("/projects/{project_id}/issues/{issue_id}/comments", response_model=CommentOut)
def reply_to_issue(
    project_id: int,
    issue_id: int,
    comment_in: CommentCreate, # 这里建议用 JSON Body
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    issue_service = IssueService(db)
    new_comment = issue_service.reply_to_issue(
        project_id=project_id,
        issue_id=issue_id,
        comment_in=comment_in,
        background_tasks=background_tasks,
        current_user=current_user
    )
    return new_comment

# 7. 获取回复列表
@router.get("/projects/{project_id}/issues/{issue_id}/comments", response_model=List[CommentOut])
def read_issue_comments(
    project_id: int,
    issue_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    issue_service = IssueService(db)
    comments = issue_service.get_comments_for_issue(
        project_id=project_id,
        issue_id=issue_id,
        current_user=current_user
    )
    return comments