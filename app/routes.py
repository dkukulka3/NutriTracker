from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_user, current_user, login_required
from datetime import date

from app.extensions import db
from app.models import User
from app.nutrition_log import (
    add_entry,
    calculate_total,
    get_goals,
    set_goals,
    get_entries_by_date,
    delete_entry,
    get_entry_by_id,
    update_entry
)

main = Blueprint("main", __name__)


def safe_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


@main.route("/")
@login_required
def home():
    today = date.today().isoformat()

    totals = calculate_total(today, current_user.id)
    goals = get_goals(current_user.id)

    calorie_percent = 0
    protein_percent = 0

    if goals:
        if goals["calorie_goal"] > 0:
            calorie_percent = min((totals["calories"] / goals["calorie_goal"]) * 100, 100)

        if goals["protein_goal"] > 0:
            protein_percent = min((totals["protein"] / goals["protein_goal"]) * 100, 100)

    return render_template(
        "home.html",
        today=today,
        totals=totals,
        goals=goals,
        calorie_percent=calorie_percent,
        protein_percent=protein_percent
    )


@main.route("/add", methods=["GET", "POST"])
@login_required
def add():
    if request.method == "POST":
        log_date = request.form.get("log_date", "").strip()
        food = request.form.get("food", "").strip()

        calories = safe_float(request.form.get("calories"))
        protein = safe_float(request.form.get("protein"))
        carbs = safe_float(request.form.get("carbs"))
        fats = safe_float(request.form.get("fats"))

        if not log_date or not food:
            return render_template("add.html", error="Date and food name are required.")

        if None in (calories, protein, carbs, fats):
            return render_template(
                "add.html",
                error="Calories, protein, carbs, and fats must all be valid numbers."
            )

        add_entry(log_date, food, calories, protein, carbs, fats, current_user.id)

        return render_template("add.html", success_message="Food added successfully!")

    return render_template("add.html")


@main.route("/totals", methods=["GET", "POST"])
@login_required
def totals():
    if request.method == "POST":
        log_date = request.form.get("log_date", "").strip()
    else:
        log_date = request.args.get("log_date", "").strip()

    if log_date:
        totals = calculate_total(log_date, current_user.id)
        entries = get_entries_by_date(log_date, current_user.id)
        goals = get_goals(current_user.id)

        calorie_percent = 0
        protein_percent = 0

        if goals:
            if goals["calorie_goal"] > 0:
                calorie_percent = min((totals["calories"] / goals["calorie_goal"]) * 100, 100)

            if goals["protein_goal"] > 0:
                protein_percent = min((totals["protein"] / goals["protein_goal"]) * 100, 100)

        return render_template(
            "totals.html",
            totals=totals,
            entries=entries,
            log_date=log_date,
            goals=goals,
            calorie_percent=calorie_percent,
            protein_percent=protein_percent
        )

    return render_template("totals.html", totals=None, goals=None)


@main.route("/delete/<int:entry_id>", methods=["POST"])
@login_required
def delete(entry_id):
    log_date = request.form.get("log_date")

    delete_entry(entry_id, current_user.id)

    return redirect(url_for("main.totals", log_date=log_date))


@main.route("/edit/<int:entry_id>", methods=["GET", "POST"])
@login_required
def edit(entry_id):
    entry = get_entry_by_id(entry_id, current_user.id)

    if entry is None:
        return "Entry not found."

    if request.method == "POST":
        log_date = request.form.get("log_date", "").strip()
        food = request.form.get("food", "").strip()

        calories = safe_float(request.form.get("calories"))
        protein = safe_float(request.form.get("protein"))
        carbs = safe_float(request.form.get("carbs"))
        fats = safe_float(request.form.get("fats"))

        if not log_date or not food:
            return render_template(
                "edit.html",
                entry=entry,
                error="Date and food name are required."
            )

        if None in (calories, protein, carbs, fats):
            return render_template(
                "edit.html",
                entry=entry,
                error="Calories, protein, carbs, and fats must all be valid numbers."
            )

        update_entry(
            entry_id,
            log_date,
            food,
            calories,
            protein,
            carbs,
            fats,
            current_user.id
        )

        return redirect(url_for("main.totals", log_date=log_date))

    return render_template("edit.html", entry=entry)


@main.route("/goals", methods=["GET", "POST"])
@login_required
def goals():
    if request.method == "POST":
        calorie_goal = safe_float(request.form.get("calorie_goal"))
        protein_goal = safe_float(request.form.get("protein_goal"))

        if calorie_goal is None or protein_goal is None:
            return render_template(
                "goals.html",
                error="Both goals must be valid numbers."
            )

        set_goals(calorie_goal, protein_goal, current_user.id)

        return render_template(
            "goals.html",
            success_message="Goals saved successfully!"
        )

    return render_template("goals.html")


@main.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        if not username or not email or not password:
            return render_template(
                "register.html",
                error="Username, email, and password are required."
            )

        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()

        if existing_user:
            return render_template(
                "register.html",
                error="Username or email already exists."
            )

        new_user = User(
            username=username,
            email=email
        )

        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("main.login"))

    return render_template("register.html")


@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        if not email or not password:
            return render_template(
                "login.html",
                error="Email and password are required."
            )

        user = User.query.filter_by(email=email).first()

        if user is None or not user.check_password(password):
            return render_template(
                "login.html",
                error="Invalid email or password."
            )

        login_user(user)

        return redirect(url_for("main.home"))

    return render_template("login.html")