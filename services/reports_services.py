import json
import markdown
from sqlalchemy.orm import Session

from domain_models.neurology_models import Metric, Question, ReportKey
from repository.reports_repository import create_predicted_report, get_all_reports, get_report_by_id, \
    get_predicted_reports, create_feedback, update_diagnosis_report
from retrieval.diagnosis_and_category_retriever import generate_diagnosis_report
from retrieval.p1_anamnesia_retrieval import generate_neurology_report
from view_models.ReportViewModel import ReportViewModel



def create_and_save_generated_report(case_name: str, anamnesis: str, db: Session):
    report = generate_neurology_report(anamnesis)
    return create_predicted_report(db, case_name, report.compressed_summary, json.loads(report.model_dump_json()))

def create_and_save_diagnosis(case_name: str, answer: str, db: Session):
    report = generate_diagnosis_report(answer)
    return update_diagnosis_report(db, case_name, json.loads(report.model_dump_json()))

def list_actual_reports(db: Session):
    return get_all_reports(db)


def get_actual_report(report_id: int, db: Session):
    return get_report_by_id(report_id, db)


def get_report_with_viewmodel(report_id: int, predicted_report_id: int, db: Session):
    actual_report = get_report_by_id(report_id, db)
    if not actual_report:
        return None

    predicted_reports = get_predicted_reports(report_id, db)
    predicted = next((r for r in predicted_reports if r.id == predicted_report_id), None) if predicted_report_id else \
        predicted_reports[0] if predicted_reports else None
    if not predicted:
        return None

    questions_by_section = {}
    for key in actual_report.full_report.keys():
        if key != 'pathophysiologies':
            metric = db.query(Metric).filter(Metric.name == key).first()
            if metric:
                questions = db.query(Question).filter(Question.metric_id == metric.id).all()
                questions_by_section[key] = questions

    return ReportViewModel(
        actual_report=actual_report,
        predicted_report=predicted,
        all_predicted_reports=predicted_reports,
        questions_by_section=questions_by_section
    )


def get_second_phase_report(report_id: int, predicted_report_id: int, db: Session):
    actual_report = get_report_by_id(report_id, db)
    if not actual_report:
        return None

    predicted_reports = get_predicted_reports(report_id, db)
    predicted = next((r for r in predicted_reports if r.id == predicted_report_id), None) if predicted_report_id else \
        predicted_reports[0] if predicted_reports else None
    if not predicted:
        return None

    questions_by_section = {}
    view_model = ReportViewModel(
        actual_report=actual_report,
        predicted_report=predicted,
        all_predicted_reports=predicted_reports,
        questions_by_section=questions_by_section
    )

    for report in [view_model.actual_report, view_model.predicted_report]:
        pe = report.physical_examination_report
        if pe and "llm_output" in pe:
            pe["llm_output_html"] = markdown.markdown(pe["llm_output"])

    return view_model


def submit_feedback_data(form_data, predicted_report_id, actual_report_id, db: Session, user_id: int = 1):
    report_key_cache = {}
    handled_ids = set()

    def get_report_key_id(metric_name: str):
        """Helper to get or cache report_key_id."""
        if metric_name not in report_key_cache:
            rk = db.query(ReportKey).filter(ReportKey.key_path == metric_name).first()
            if rk:
                report_key_cache[metric_name] = rk.id
        return report_key_cache.get(metric_name)

    for key, value in form_data.items():
        if key.startswith("rating_"):
            question_id = int(key.split("_")[1])
            handled_ids.add(question_id)
            question = db.query(Question).filter(Question.id == question_id).first()
            if not question or question.type != "numeric":
                continue
            rating = int(value)
            comment = None

        elif key.startswith("comment_"):
            question_id = int(key.split("_")[1])
            if question_id in handled_ids:
                continue  # already handled in rating
            question = db.query(Question).filter(Question.id == question_id).first()
            if not question or question.type != "textual":
                continue
            rating = None
            comment = value

        else:
            continue

        metric = db.query(Metric).filter(Metric.id == question.metric_id).first()
        if not metric:
            continue

        # Primary report key
        primary_key_id = get_report_key_id(metric.name)
        if primary_key_id:
            create_feedback(db, user_id, predicted_report_id, primary_key_id, question_id, rating, comment)

        # Duplicate answers for "anatomical_localisations" to "pathophysiologies"
        if metric.name == "anatomical_localisations":
            secondary_key_id = get_report_key_id("pathophysiologies")
            if secondary_key_id:
                create_feedback(db, user_id, predicted_report_id, secondary_key_id, question_id, rating, comment)

    db.commit()


def delete_report_by_id(report_id: int, db: Session):
    report = get_report_by_id(report_id, db)
    if report:
        db.delete(report)
        db.commit()
        return True
    return False
