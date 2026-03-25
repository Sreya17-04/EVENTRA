from database import db
from datetime import datetime, date, time
class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # student / coordinator / admin


class Hall(db.Model):
    __tablename__ = "hall"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    capacity = db.Column(db.Integer)
    location = db.Column(db.String(200))


class Event(db.Model):
    __tablename__ = "event"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200))
    description = db.Column(db.Text)

    date = db.Column(db.Date)
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)

    status = db.Column(db.String(20), default="pending")

    student_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    hall_id = db.Column(db.Integer, db.ForeignKey('hall.id'))

    student = db.relationship("User", foreign_keys=[student_id])
    hall = db.relationship("Hall", foreign_keys=[hall_id])

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Approval(db.Model):
    __tablename__ = "approval"

    id = db.Column(db.Integer, primary_key=True)

    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    approved_by = db.Column(db.Integer, db.ForeignKey('user.id'))

    decision = db.Column(db.String(20))
    remarks = db.Column(db.Text)

    decision_time = db.Column(db.DateTime, default=datetime.utcnow)

    event = db.relationship("Event", backref="approvals")
    approver = db.relationship("User", foreign_keys=[approved_by])