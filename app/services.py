from datetime import datetime
from zoneinfo import ZoneInfo
from fastapi import HTTPException
from .database import conn, lock
from .models import BookingResponse, BookingInfo, FitnessClass

IST = ZoneInfo("Asia/Kolkata")

def convert_to_timezone(ist_dt: datetime, tz_name: str) -> datetime:
    try:
        tz = ZoneInfo(tz_name)
    except Exception:
        tz = IST
    return ist_dt.astimezone(tz)

def list_classes(timezone: str):
    with lock:
        cur = conn.cursor()
        cur.execute("SELECT * FROM classes ORDER BY datetime ASC")
        rows = cur.fetchall()
    classes = []
    for r in rows:
        dt_ist = datetime.fromisoformat(r["datetime"]).replace(tzinfo=IST)
        dt_local = convert_to_timezone(dt_ist, timezone)
        classes.append(FitnessClass(
            id=r["id"],
            name=r["name"],
            datetime=dt_local.isoformat(),
            instructor=r["instructor"],
            available_slots=r["available_slots"]
        ))
    return classes

def create_booking(class_id: int, client_name: str, client_email: str):
    with lock:
        cur = conn.cursor()
        cur.execute("SELECT available_slots FROM classes WHERE id = ?", (class_id,))
        cls = cur.fetchone()
        if not cls:
            raise HTTPException(status_code=404, detail="Class not found")
        if cls["available_slots"] <= 0:
            raise HTTPException(status_code=400, detail="No slots available")
        booking_time = datetime.utcnow().isoformat() + "Z"
        cur.execute(
            "INSERT INTO bookings (class_id, client_name, client_email, booking_time) VALUES (?, ?, ?, ?)",
            (class_id, client_name, client_email, booking_time)
        )
        cur.execute(
            "UPDATE classes SET available_slots = available_slots - 1 WHERE id = ?",
            (class_id,)
        )
        conn.commit()
        booking_id = cur.lastrowid
    return BookingResponse(
        booking_id=booking_id,
        class_id=class_id,
        client_name=client_name,
        client_email=client_email,
        booking_time=booking_time
    )

def get_bookings_by_email(email: str):
    with lock:
        cur = conn.cursor()
        cur.execute("SELECT * FROM bookings WHERE client_email = ? ORDER BY booking_time DESC", (email,))
        rows = cur.fetchall()
    bookings = []
    for r in rows:
        bookings.append(BookingInfo(
            id=r["id"],
            class_id=r["class_id"],
            client_name=r["client_name"],
            client_email=r["client_email"],
            booking_time=r["booking_time"]
        ))
    return bookings
