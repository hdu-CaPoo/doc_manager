from typing import List
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session

from app.crud.issue import create_issue, get_issues_by_project, get_issue_by_id, update_issue, delete_issue # 导入 CRUD
from app.crud.member import get_member # 导入成员检查函数

from app.schemas.issue import IssueOut, CommentOut, CommentCreate
from app.crud.issue import create_comment, get_comments_by_issue
from app.models.issue import Issue

from app.core.email import send_notification_email

from app.crud.project import get_project # 复用检查项目是否存在的逻辑

from app.api.deps import get_db, get_current_user
from app.models.user import User

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
    # 1. 检查项目是否存在
    project = get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    # 2. 检查用户是否为项目成员
    member = get_member(db, project_id, current_user.id)
    if not member:
        raise HTTPException(status_code=403, detail="你不是该项目成员")
    
    # 3. 创建提问
    new_issue = create_issue(
        db,
        project_id=project_id,
        creator_id=current_user.id,
        title=title,
        content=content,
        priority=priority
    )
    return new_issue

# 2. 获取项目的所有提问
@router.get("/projects/{project_id}/issues", response_model=List[IssueOut])
def read_issues_by_project(
    project_id: int,
    status: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. 检查项目是否存在
    project = get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    # 2. 检查用户是否为项目成员
    member = get_member(db, project_id, current_user.id)
    if not member:
        raise HTTPException(status_code=403, detail="你不是该项目成员")
    
    # 3. 获取提问列表
    issues = get_issues_by_project(db, project_id, status)
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
    # 1. 检查项目是否存在
    project = get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    # 2. 检查用户是否为项目成员
    member = get_member(db, project_id, current_user.id)
    if not member:
        raise HTTPException(status_code=403, detail="你不是该项目成员")
    
    # 3. 获取提问
    issue = get_issue_by_id(db, issue_id)
    if not issue or issue.project_id != project_id:
        raise HTTPException(status_code=404, detail="提问不存在")
    
    # 4. 更新提问
    updated_issue = update_issue(
        db,
        db_issue=issue,
        new_status=new_status,
        new_content=new_content
    )

    if new_status and new_status != issue.status:
        creator_email = issue.creator.email
        
        background_tasks.add_task(
            send_notification_email, 
            creator_email, 
            f"问题状态更新: [{issue.title}]", 
            "状态变更", 
            f"你的问题状态已更新为: {updated_issue.status}", 
            f"http://your-frontend.com/issues/{issue_id}"
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
    # 1. 检查项目是否存在
    project = get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    # 2. 检查用户是否为项目管理员或拥有者或提问者本人
    member = get_member(db, project_id, current_user.id)
    if not member or (member.role not in ["admin", "owner"] and issue.creator_id != current_user.id):
        raise HTTPException(status_code=403, detail="你不是该项目管理员或拥有者或提问者本人")
    
    # 3. 获取提问
    issue = get_issue_by_id(db, issue_id)
    if not issue or issue.project_id != project_id:
        raise HTTPException(status_code=404, detail="提问不存在")
    
    # 4. 删除提问
    delete_issue(db, issue)
    return {"msg": "提问已删除"}

# 5. 获取单个提问
@router.get("/projects/{project_id}/issues/{issue_id}", response_model=IssueOut)
def read_single_issue(
    project_id: int,
    issue_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. 检查项目是否存在
    project = get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    # 2. 检查用户是否为项目成员
    member = get_member(db, project_id, current_user.id)
    if not member:
        raise HTTPException(status_code=403, detail="你不是该项目成员")
    
    # 3. 获取提问
    issue = get_issue_by_id(db, issue_id)
    if not issue or issue.project_id != project_id:
        raise HTTPException(status_code=404, detail="提问不存在")
    
    return issue


# --- 新增：发表回复 ---
@router.post("/projects/{project_id}/issues/{issue_id}/comments", response_model=CommentOut)
def reply_to_issue(
    project_id: int,
    issue_id: int,
    comment_in: CommentCreate, # 这里建议用 JSON Body
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. 检查 Issue 是否存在
    issue = get_issue_by_id(db, issue_id)
    if not issue or issue.project_id != project_id:
        raise HTTPException(status_code=404, detail="问题不存在")
    
    # 2. 检查权限 (必须是该项目的成员才能回复)
    # 我们可以通过 issue.project_id 找到项目，然后查成员表
    member = get_member(db, issue.project_id, current_user.id)
    if not member:
        raise HTTPException(status_code=403, detail="你不是该项目成员，无法回复")


    # 4. 发送通知邮件 (后台任务)
    # --- 邮件通知逻辑 ---
    # 1. 只有当回复人不是提问者本人时，才发邮件
    if current_user.id != issue.creator_id:
        # 获取提问者的邮箱
        # 这里需要保证 issue.creator 已经加载了，或者重新查一遍 user
        creator_email = issue.creator.email 
        
        email_subject = f"你的问题 [{issue.title}] 有新回复"
        email_content = f"{current_user.nickname} 回复了你：{comment_in.content[:50]}..."
        link = f"http://your-frontend-domain.com/issues/{issue_id}" # 前端地址

        background_tasks.add_task(
            send_notification_email, 
            creator_email, 
            email_subject, 
            "你有新回复", 
            email_content, 
            link
        )

    return create_comment(
        db,
        issue_id=issue_id,
        user_id=current_user.id,
       content=comment_in.content
    )

# --- 新增：获取回复列表 ---
# (其实如果你在 IssueOut 里加了 comments 字段，这个接口也可以省掉，看你需求)
@router.get("/projects/{project_id}/issues/{issue_id}/comments", response_model=List[CommentOut])
def read_issue_comments(
    project_id: int,
    issue_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. 检查 Issue 是否存在
    issue = get_issue_by_id(db, issue_id)
    if not issue or issue.project_id != project_id:
        raise HTTPException(status_code=404, detail="问题不存在")
        
    # 2. 检查权限
    member = get_member(db, issue.project_id, current_user.id)
    if not member:
        raise HTTPException(status_code=403, detail="你不是该项目成员")

    return get_comments_by_issue(db, issue_id)