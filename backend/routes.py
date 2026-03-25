from flask import Blueprint, request, jsonify
from models import Event, Approval, User
from database import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

main_routes = Blueprint("main", __name__)


# CREATE EVENT
@main_routes.route("/create_event", methods=["POST"])
@jwt_required()
def create_event():

    user_id = get_jwt_identity()
    data = request.json

    user = User.query.get(user_id)

    if user.role != "student":
        return jsonify({"message": "Only students can create events"}), 403

    # Convert date/time strings to proper format
    date_val = datetime.strptime(data["date"], "%Y-%m-%d").date()
    start_time_val = datetime.strptime(data["start_time"], "%H:%M").time()
    end_time_val = datetime.strptime(data["end_time"], "%H:%M").time()

    # Conflict detection
    conflict = Event.query.filter(
        Event.hall_id == data["hall_id"],
        Event.date == date_val,
        Event.start_time < end_time_val,
        Event.end_time > start_time_val
    ).first()

    if conflict:
        return jsonify({"message": "Hall already booked"}), 400

    event = Event(
        title=data["title"],
        description=data["description"],
        date=date_val,
        start_time=start_time_val,
        end_time=end_time_val,
        student_id=user_id,
        hall_id=data["hall_id"]
    )

    db.session.add(event)
    db.session.commit()

    return jsonify({"message": "Event created successfully"})


# APPROVE / REJECT EVENT
@main_routes.route("/approve_event/<int:event_id>", methods=["POST"])
@jwt_required()
def approve_event(event_id):

    user_id = get_jwt_identity()
    data = request.json

    user = User.query.get(user_id)

    if user.role not in ["coordinator", "admin"]:
        return jsonify({"message": "Not authorized"}), 403

    event = Event.query.get(event_id)

    if not event:
        return jsonify({"message": "Event not found"}), 404

    event.status = data["decision"]

    approval = Approval(
        event_id=event_id,
        approved_by=user_id,
        decision=data["decision"],
        remarks=data.get("remarks", "")
    )

    db.session.add(approval)
    db.session.commit()

    return jsonify({"message": "Decision recorded successfully"})


# GET EVENTS
@main_routes.route("/get_events", methods=["GET"])
@jwt_required()
def get_events():

    user_id = get_jwt_identity()

    user = User.query.get(user_id)

    if user.role == "student":
        events = Event.query.filter_by(student_id=user_id).all()
    else:
        events = Event.query.all()

    return jsonify([
        {
            "id": e.id,
            "title": e.title,
            "date": str(e.date),
            "status": e.status,
            "hall_id": e.hall_id
        }
        for e in events
    ])