from datetime import date

from pydantic import Field, model_validator

from app.schemas.common import BaseSchema


class BookingDates(BaseSchema):
    checkin: date
    checkout: date

    @model_validator(mode="after")
    def check_dates(self) -> "BookingDates":
        if self.checkin >= self.checkout:
            raise ValueError("Check-in date must be before check-out date")
        return self


class Booking(BaseSchema):
    first_name: str = Field(alias="firstname", min_length=1)
    last_name: str = Field(alias="lastname", min_length=1)
    total_price: int = Field(alias="totalprice", gt=0)
    deposit_paid: bool = Field(alias="depositpaid")
    booking_dates: BookingDates = Field(alias="bookingdates")
    additional_needs: str | None = Field(default=None, alias="additionalneeds")


class BookingResponse(BaseSchema):
    bookingid: int
    booking: Booking
