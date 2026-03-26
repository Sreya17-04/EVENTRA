from flask import Blueprint, request, jsonify
from models import Event, Approval, User, Hall
from database import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from sqlalchemy.orm import joinedload

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

    if user.role == "coordinator":
        if data["decision"] == "approved":
            event.status = "coord_approved"
        else:
            event.status = "rejected"

    elif user.role == "admin":
        if data["decision"] == "approved":
            event.status = "final_approved"
        else:
            event.status = "rejected"

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
        events = Event.query.filter_by(student_id=user_id).options(joinedload(Event.hall)).all()
    else:
        events = Event.query.options(joinedload(Event.hall), joinedload(Event.student)).all()

    return jsonify([
        {
            "id": e.id,
            "title": e.title,
            "description": e.description,
            "date": str(e.date),
            "start_time": str(e.start_time),
            "end_time": str(e.end_time),
            "status": e.status,
            "hall": {
                "id": e.hall.id,
                "name": e.hall.name
            },
            "student": {
                "id": e.student.id,
                "username": e.student.username
            } if user.role != "student" else None
        }
        for e in events
    ])


# GET HALLS
@main_routes.route("/get_halls", methods=["GET"])
def get_halls():
    halls = Hall.query.all()
    return jsonify([
        {
            "id": h.id,
            "name": h.name,
            "capacity": h.capacity,
            "location": h.location
        }
        for h in halls
    ])


# GET PENDING APPROVALS (for coordinators and admins)
@main_routes.route("/get_pending_approvals", methods=["GET"])
@jwt_required()
def get_pending_approvals():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if user.role not in ["coordinator", "admin"]:
        return jsonify({"message": "Not authorized"}), 403

    # For coordinators: get events that are pending or coord_approved
    # For admins: get coord_approved events
    if user.role == "coordinator":
        events = Event.query.filter(Event.status.in_(["pending", "coord_approved"])).all()
    else:  # admin
        events = Event.query.filter_by(status="coord_approved").all()

    return jsonify([
        {
            "id": e.id,
            "title": e.title,
            "description": e.description,
            "date": str(e.date),
            "start_time": str(e.start_time),
            "end_time": str(e.end_time),
            "status": e.status,
            "hall": {
                "id": e.hall.id,
                "name": e.hall.name,
                "location": e.hall.location
            },
            "student": {
                "id": e.student.id,
                "username": e.student.username,
                "email": e.student.email
            }
        }
        for e in events
    ])


@main_routes.route("/approval_history/<int:event_id>", methods=["GET"])
@jwt_required()
def get_approval_history(event_id):

    approvals = Approval.query.filter_by(event_id=event_id).all()

    result = []

    for a in approvals:
        user = User.query.get(a.approved_by)

        result.append({
            "role": user.role,
            "decision": a.decision,
            "remarks": a.remarks,
            "time": str(a.decision_time)
        })

    return jsonify(result)


# GET ANALYTICS (for admin)
@main_routes.route("/get_analytics", methods=["GET"])
@jwt_required()
def get_analytics():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if user.role != "admin":
        return jsonify({"message": "Not authorized"}), 403

    total = Event.query.count()
    approved = Event.query.filter_by(status="final_approved").count()
    pending = Event.query.filter(Event.status.in_(["pending", "coord_approved"])).count()
    rejected = Event.query.filter_by(status="rejected").count()

    return jsonify({
        "total": total,
        "approved": approved,
        "pending": pending,
        "rejected": rejected
    })