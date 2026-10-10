from fastapi import FastAPI
from fastapi import HTTPException
from database import get_connection
from pydantic import BaseModel
from datetime import date

class Company(BaseModel):
    id: int
    name: str
    city: str | None = None
    description: str | None = None

class CompanyCreate(BaseModel):
    name: str
    city: str | None = None
    description: str | None = None

class CompanyUpdate(BaseModel):
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

class JobUpdate(BaseModel):
    title: str
    description: str
    company_id: int
    city: str | None = None
    salary: str | None = None
    duration: str | None = None
    start_date: date | None = None
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


@app.post("/companies", response_model=Company)
def create_company(company: CompanyCreate):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO companies (name, city, description)
        VALUES (%s, %s, %s)
        RETURNING id, name, city, description
    """, (
        company.name,
        company.city,
        company.description
    ))

    new_company = cursor.fetchone()

    connection.commit()
    cursor.close()
    connection.close()

    return {
        "id": new_company[0],
        "name": new_company[1],
        "city": new_company[2],
        "description": new_company[3]
    }


@app.get("/companies/{company_id}", response_model=Company)
def get_company(company_id: int):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, name, city, description
        FROM companies
        WHERE id = %s
    """, (company_id,))

    company = cursor.fetchone()

    cursor.close()
    connection.close()

    if company is None:
        raise HTTPException(
            status_code=404,
            detail="Entreprise introuvable"
        )

    return {
        "id": company[0],
        "name": company[1],
        "city": company[2],
        "description": company[3]
    }


@app.put("/companies/{company_id}", response_model=Company)
def update_company(company_id: int, company: CompanyUpdate):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE companies
        SET name = %s, city = %s, description = %s
        WHERE id = %s
        RETURNING id, name, city, description
        """,
        (company.name, company.city, company.description, company_id)
    )

    updated_company = cur.fetchone()

    conn.commit()
    cur.close()
    conn.close()

    if updated_company is None:
        raise HTTPException(status_code=404, detail="Entreprise introuvable")

    return {
        "id": updated_company[0],
        "name": updated_company[1],
        "city": updated_company[2],
        "description": updated_company[3]
    }

@app.delete("/companies/{company_id}")
def delete_company(company_id: int):
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            "DELETE FROM companies WHERE id = %s RETURNING id",
            (company_id,)
        )
        deleted_company = cur.fetchone()

        if deleted_company is None:
            raise HTTPException(
                status_code=404,
                detail="Entreprise introuvable"
            )

        conn.commit()

        return {
            "message": "Entreprise supprimée avec succès",
            "id": deleted_company[0]
        }

    except HTTPException:
        conn.rollback()
        raise

    except Exception:
        conn.rollback()
        raise HTTPException(
            status_code=409,
            detail="Impossible de supprimer cette entreprise. Vérifiez si des offres lui sont associées."
        )

    finally:
        cur.close()
        conn.close()

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

@app.get("/jobs/{job_id}", response_model=Job)
def get_job(job_id: int):
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
        WHERE id = %s
    """, (job_id,))

    job = cursor.fetchone()

    cursor.close()
    connection.close()

    if job is None:
        raise HTTPException(status_code=404, detail="Offre introuvable")

    return {
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

@app.put("/jobs/{job_id}", response_model=Job)
def update_job(job_id: int, job: JobUpdate):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE jobs
        SET title = %s,
            description = %s,
            company_id = %s,
            city = %s,
            salary = %s,
            duration = %s,
            start_date = %s,
            education_level = %s
        WHERE id = %s
        RETURNING id, title, description, company_id, city,
                  salary, duration, start_date, education_level
    """, (
        job.title,
        job.description,
        job.company_id,
        job.city,
        job.salary,
        job.duration,
        job.start_date,
        job.education_level,
        job_id
    ))

    updated_job = cursor.fetchone()
    connection.commit()
    cursor.close()
    connection.close()

    if updated_job is None:
        raise HTTPException(status_code=404, detail="Offre introuvable")

    return {
        "id": updated_job[0],
        "title": updated_job[1],
        "description": updated_job[2],
        "company_id": updated_job[3],
        "city": updated_job[4],
        "salary": updated_job[5],
        "duration": updated_job[6],
        "start_date": str(updated_job[7]) if updated_job[7] else None,
        "education_level": updated_job[8]
    }


@app.delete("/jobs/{job_id}")
def delete_job(job_id: int):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM jobs WHERE id = %s RETURNING id",
        (job_id,)
    )

    deleted_job = cursor.fetchone()

    connection.commit()
    cursor.close()
    connection.close()

    if deleted_job is None:
        raise HTTPException(status_code=404, detail="Offre introuvable")

    return {
        "message": "Offre supprimée avec succès",
        "id": deleted_job[0]
    }
