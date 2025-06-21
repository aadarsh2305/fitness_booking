from pydantic import BaseModel, EmailStr, Field

class FitnessClass(BaseModel):
    id: int
    name: str
    datetime: str
    instructor: str
    available_slots: int

class BookingRequest(BaseModel):
    class_id: int = Field(..., gt=0)
    client_name: str = Field(..., min_length=1)
    client_email: EmailStr

class BookingResponse(BaseModel):
    booking_id: int
    class_id: int
    client_name: str
    client_email: EmailStr
    booking_time: str

class BookingInfo(BaseModel):
    id: int
    class_id: int
    client_name: str
    client_email: EmailStr
    booking_time: str
