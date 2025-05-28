from datetime import date
from sqlalchemy import Column, Integer, Boolean, Date, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
from datetime import date
from sqlalchemy.orm import joinedload

from core import AppContext
from .user import Users

Base = declarative_base()


class Attendance(Base):
    __tablename__ = "attendances"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(Users.id), nullable=False)
    present = Column(Boolean, nullable=False, default=False)
    date = Column(Date, nullable=False, default=date.today)  # Default to today's date

    user = relationship(Users, backref="attendances")


class AttendanceRepository:
    def __init__(self, ctx: AppContext):
        self.ctx = ctx
        self.db = ctx.db

    def mark_attendance(self, user_id: int, present: bool):
        """Marks the attendance for today for a given user."""
        today = date.today()

        existing = self.db.find(Attendance, user_id=user_id, date=today)

        # Only create if not already marked
        if not existing:
            self.db.create(Attendance(user_id=user_id, present=present, date=today))

    def get_users_not_present_today(self):
        """Get the list of users who are not present today."""
        today = date.today()
        # Query users who are absent today (present == False)
        session = self.db.get_session()
        absent_users = (
            session.query(Users)
            .outerjoin(
                Attendance,
                (Attendance.user_id == Users.id) & (Attendance.date == today),
            )
            .filter(Attendance.id.is_(None))
            .all()
        )
        return [user for user in absent_users]

    def get_users_present_today(self):
        """Get the list of users who are present today."""
        today = date.today()

        present_users = self.db.find_all(
            Attendance,
            date=today,
            present=True,
            options=[joinedload(Attendance.user)],
        )
        print(f"Present users count: {len(present_users)}")
        return [attendance.user for attendance in present_users]
