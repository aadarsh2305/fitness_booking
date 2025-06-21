from fastapi import FastAPI, Query, HTTPException
from typing import List, Optional
from . import database, services, models

app = FastAPI()

@app.on_event("startup")
def startup():
    database.init_db()
    database.seed_db()

@app.get("/classes", response_model=List[models.FitnessClass])
def get_classes(timezone: Optional[str] = Query("Asia/Kolkata")):
    return services.list_classes(timezone)

@app.post("/book", response_model=models.BookingResponse)
def book_class(request: models.BookingRequest):
    try:
        return services.create_booking(request.class_id, request.client_name, request.client_email)
    except HTTPException as e:
        raise e
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/bookings", response_model=List[models.BookingInfo])
def bookings(client_email: str = Query(...)):
    return services.get_bookings_by_email(client_email)
