from http.client import HTTPException
from typing import List, Optional

from fastapi import APIRouter, Depends, Form
from requests import Session
from fastapi import Request
from starlette import status
from starlette.responses import HTMLResponse, RedirectResponse, JSONResponse
from starlette.templating import Jinja2Templates

from database.database import get_db
from schemas.neurology_schema import ReportSummary
from services.reports_services import list_actual_reports, create_and_save_generated_report, get_report_with_viewmodel, \
    submit_feedback_data, delete_report_by_id, get_actual_report, get_second_phase_report

router = APIRouter()


templates = Jinja2Templates(directory="templates")
# templates.env.filters['sort_custom'] = sort_report_keys


@router.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    reports = list_actual_reports(db)
    return templates.TemplateResponse("dashboard.html", {"request": request, "reports": reports})


@router.get("/report/create", response_class=HTMLResponse)
def create_report_form(request: Request):
    return templates.TemplateResponse("create_report.html", {"request": request})


@router.post("/report/create")
def create_report(case_name: str = Form(...), anamnesis: str = Form(...), db: Session = Depends(get_db)):
    report = create_and_save_generated_report(case_name, anamnesis, db)
    return RedirectResponse(url=f"/report/{report.id}", status_code=303)


@router.get("/reports", response_model=List[ReportSummary])
def list_reports(db: Session = Depends(get_db)):
    return list_actual_reports(db)


@router.get("/reports/{report_id}", response_class=JSONResponse)
def get_report(report_id: int, db: Session = Depends(get_db)):
    report = get_actual_report(report_id, db)
    if report:
        return report.full_report
    return JSONResponse(status_code=404, content={"error": "Report not found"})


@router.get("/report/{report_id}", response_class=HTMLResponse)
def view_report(report_id: int, request: Request, predicted_report_id: Optional[int] = None, db: Session = Depends(get_db)):
    view_model = get_report_with_viewmodel(report_id, predicted_report_id, db)
    if not view_model:
        return HTMLResponse(content="Report not found", status_code=404)
    return templates.TemplateResponse("report_detail.html", {"request": request, "report": view_model})


@router.post("/submit-feedback")
async def submit_feedback(request: Request, predicted_report_id: int = Form(...), actual_report_id: int = Form(...), db: Session = Depends(get_db)):
    form_data = await request.form()
    submit_feedback_data(form_data, predicted_report_id, actual_report_id, db)
    return RedirectResponse(f"/report/{actual_report_id}?predicted_report_id={predicted_report_id}", status_code=303)


@router.get("/second_report/{report_id}", response_class=HTMLResponse)
def view_report(report_id: int, request: Request, predicted_report_id: Optional[int] = None, db: Session = Depends(get_db)):
    view_model = get_second_phase_report(report_id, predicted_report_id, db)
    if not view_model:
        return HTMLResponse(content="Report not found", status_code=404)
    return templates.TemplateResponse("second_phase_report_details.html", {"request": request, "report": view_model})


@router.post("/report/{report_id}/delete")
def delete_report(report_id: int, db: Session = Depends(get_db)):
    deleted = delete_report_by_id(report_id, db)
    if not deleted:
        return HTMLResponse(content="Report not found", status_code=404)
    return RedirectResponse(url="/", status_code=303)