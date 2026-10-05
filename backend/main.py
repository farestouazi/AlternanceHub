from fastapi import FastAPI
from database import get_connection
from pydantic import BaseModel

class Company(BaseModel):
    id: int
    name: str
    city: str | None = None
    description: str | None = None

class Job(BaseModel):
    id: int
    title: str
    description: str
    company_id: int
    city: str | None = None
    salary: str | None = None
    duration: str | None = None
    start_date: str | None = None
    education_level: str | None = None

class JobCreate(BaseModel):
    title: str
    description: str
    company_id: int
    city: str | None = None
    salary: str | None = None
    duration: str | None = None
    start_date: str | None = None
    education_level: str | None = None

app = FastAPI()

@app.get("/")
def home():
    connection = get_connection()

    connection.close()

    return {"message": "Bienvenue sur AlternanceHub !"}

@app.get("/companies", response_model=list[Company])
def get_companies():
    connection = get_connection()

    cursor = connection.cursor()
    cursor.execute("SELECT id, name, city, description FROM companies")

    companies = cursor.fetchall()

    companies = [
        {
            "id": company[0],
            "name": company[1],
            "city": company[2],
            "description": company[3]
        }
        for company in companies
    ]

    cursor.close()
    connection.close()

    return companies

@app.get("/jobs", response_model=list[Job])
def get_jobs():
    connection = get_connection()

    cursor = connection.cursor()
    cursor.execute("""
        SELECT
            id,
            title,
            description,
            company_id,
            city,
            salary,
            duration,
            start_date,
            education_level
        FROM jobs
    """)

    jobs = cursor.fetchall()

    jobs = [
        {
            "id": job[0],
            "title": job[1],
            "description": job[2],
            "company_id": job[3],
            "city": job[4],
            "salary": job[5],
            "duration": job[6],
            "start_date": str(job[7]) if job[7] else None,
            "education_level": job[8]
        }
        for job in jobs
    ]

    cursor.close()
    connection.close()

    return jobs

@app.post("/jobs", response_model=Job)
def create_job(job: JobCreate):
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO jobs (
            title,
            description,
            company_id,
            city,
            salary,
            duration,
            start_date,
            education_level
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    """, (
        job.title,
        job.description,
        job.company_id,
        job.city,
        job.salary,
        job.duration,
        job.start_date,
        job.education_level
    ))

    job_id = cursor.fetchone()[0]

    connection.commit()

    cursor.close()
    connection.close()

    return {
        "id": job_id,
        **job.model_dump()
    }