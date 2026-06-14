from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def create_audit_log(
    db: Session,
    user_id: int,
    company_id: int | None,
    action: str
):

    log = AuditLog(
        user_id=user_id,
        company_id=company_id,
        action=action
    )

    db.add(log)
    db.commit()