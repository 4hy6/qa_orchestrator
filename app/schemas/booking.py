from datetime import date

from pydantic import Field

from app.schemas.common import BaseSchema


class BookingDates(BaseSchema):
    checkin: date
    checkout: date


class Booking(BaseSchema):
    first_name: str = Field(alias="firstname")
    last_name: str = Field(alias="lastname")
    total_price: int = Field(alias="totalprice")
    deposit_paid: bool = Field(alias="depositpaid")
    booking_dates: BookingDates = Field(alias="bookingdates")
    additional_needs: str | None = Field(default=None, alias="additionalneeds")


class BookingResponse(BaseSchema):
    bookingid: int
    booking: Booking
