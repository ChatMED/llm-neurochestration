import pandas as pd

from database.database import get_db, SessionLocal
from services.reports_services import create_and_save_diagnosis

df = pd.read_csv("../data/extracted_data.csv")

db = SessionLocal()

def update_answers(row):
    case_name = row["document"]
    answer = row['Answers']
    create_and_save_diagnosis(case_name, answer, db)

df = df.apply(lambda row: update_answers(row), axis=1)

