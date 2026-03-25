from app import app
from database import db
from models import User, Hall, Event, Approval
from datetime import date, time

with app.app_context():

    # =============================
    # HALL DATA
    # =============================
    if not Hall.query.first():

        halls = [
            Hall(
                name="Main Hall",
                capacity=200,
                location="Block A"
            ),
            Hall(
                name="Seminar Hall",
                capacity=100,
                location="Block B"
            ),
            Hall(
                name="Auditorium",
                capacity=500,
                location="Block C"
            )
        ]

        db.session.add_all(halls)
        db.session.commit()


    # =============================
    # EVENT DATA (Using Your Format)
    # =============================
    if not Event.query.first():

        student = User.query.filter_by(role="student").first()
        hall = Hall.query.first()

        if student and hall:

            event = Event(
                title="Tech Workshop",
                description="Python Flask Workshop Event",
                date=date(2026, 3, 20),      # YYYY, MM, DD format
                start_time=time(10, 0),     # HH, MM
                end_time=time(12, 0),
                status="pending",
                student_id=student.id,
                hall_id=hall.id
            )

            db.session.add(event)
            db.session.commit()


    # =============================
    # APPROVAL DATA
    # =============================
    if not Approval.query.first():

        event = Event.query.first()
        coordinator = User.query.filter_by(role="coordinator").first()

        if event and coordinator:

            approval = Approval(
                event_id=event.id,
                approved_by=coordinator.id,
                decision="approved",
                remarks="Event approved for testing"
            )

            db.session.add(approval)
            db.session.commit()


print("✅ Sample data inserted successfully!")