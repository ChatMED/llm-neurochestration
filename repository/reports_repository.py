import json

from sqlalchemy.orm import Session
from domain_models.neurology_models import (
    PredictedNeurologyReportRecord,
    NeurologyReportRecord,
    Feedback
)


def create_predicted_report(db: Session, name: str, summary: str, full_report: dict):
    report = PredictedNeurologyReportRecord(
        name=name,
        summary=summary,
        full_report=full_report
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report

def update_diagnosis_report(db, case_name, diagnosis_report:dict):
    report = get_report_by_name(case_name, db)
    prev_report = report.full_report
    prev_report["diagnosis"]=diagnosis_report
    report.full_report = prev_report
    # db.add(report)
    db.commit()
    db.refresh(report)
    return report


def get_all_reports(db: Session):
    return db.query(NeurologyReportRecord).order_by(NeurologyReportRecord.created_at.desc()).all()


def get_report_by_id(report_id: int, db: Session):
    return db.query(NeurologyReportRecord).filter(NeurologyReportRecord.id == report_id).first()

def get_report_by_name(name: str, db: Session):
    return db.query(NeurologyReportRecord).filter(NeurologyReportRecord.name == name).first()

def get_predicted_reports(real_report_id: int, db: Session):
    return db.query(PredictedNeurologyReportRecord).filter(
        PredictedNeurologyReportRecord.real_report_id == real_report_id
    ).all()


def create_feedback(db: Session, user_id, predicted_report_id, report_key_id, question_id, rating, comment):
    feedback = Feedback(
        user_id=user_id,
        predicted_report_id=predicted_report_id,
        report_key_id=report_key_id,
        question_id=question_id,
        rating=rating,
        comment=comment
    )
    db.add(feedback)
