from sqlalchemy.orm import Session
from app.models.issue import Issue, IssueComment

# 1. 创建新提问
def create_issue(
    db: Session,
    project_id: int,
    creator_id: int,
    title: str,
    content: str,
    priority: str = "low"
):
    db_issue = Issue(
        project_id=project_id,
        creator_id=creator_id,
        title=title,
        content=content,
        priority=priority,
        status="open"
    )
    db.add(db_issue)
    db.commit()
    db.refresh(db_issue)
    return db_issue

# 2. 获取项目的所有提问
def get_issues_by_project(db: Session, project_id: int, status: str):
    if status:
        return db.query(Issue).filter(Issue.project_id == project_id, Issue.status == status).all()
    else:
        return db.query(Issue).filter(Issue.project_id == project_id).all()

# 3. 更新提问状态或内容
def update_issue(
    db: Session,
    db_issue: Issue,
    new_status: str,
    new_content: str
):
    if new_status:
        db_issue.status = new_status #type: ignore
    if new_content:
        db_issue.content = new_content #type: ignore
    db.add(db_issue)
    db.commit()
    db.refresh(db_issue)
    return db_issue

#4. 获取单个提问
def get_issue_by_id(db: Session, issue_id: int):
    return db.query(Issue).filter(Issue.id == issue_id).first()

#5. 删除提问
def delete_issue(db: Session, db_issue: Issue):
    db.delete(db_issue)
    db.commit()



# 6. 创建评论
def create_comment(db: Session, issue_id: int, user_id: int, content: str):
    db_comment = IssueComment(
        issue_id=issue_id,
        user_id=user_id,
        content=content
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

# 7. 获取某问题的所有评论
def get_comments_by_issue(db: Session, issue_id: int):
    return db.query(IssueComment).filter(IssueComment.issue_id == issue_id).all()

# 8. 删除评论 (可选，做不做看你)
def delete_comment(db: Session, comment_id: int):
    comment = db.query(IssueComment).filter(IssueComment.id == comment_id).first()
    if comment:
        db.delete(comment)
        db.commit()