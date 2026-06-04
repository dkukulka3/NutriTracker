# Daily nutrition tracker database helper functions

from app.extensions import db
from app.models import FoodEntry, Goal
from sqlalchemy import func


def add_entry(log_date, food, calories, protein, carbs, fats, user_id):
    new_entry = FoodEntry(
        log_date=log_date,
        food=food,
        calories=calories,
        protein=protein,
        carbs=carbs,
        fats=fats,
        user_id=user_id
    )

    db.session.add(new_entry)
    db.session.commit()


def calculate_total(log_date, user_id):
    totals = db.session.query(
        func.sum(FoodEntry.calories),
        func.sum(FoodEntry.protein),
        func.sum(FoodEntry.carbs),
        func.sum(FoodEntry.fats)
    ).filter(
        FoodEntry.log_date == log_date,
        FoodEntry.user_id == user_id
    ).first()

    return {
        "calories": totals[0] or 0,
        "protein": totals[1] or 0,
        "carbs": totals[2] or 0,
        "fats": totals[3] or 0
    }


def get_entries_by_date(log_date, user_id):
    entries = FoodEntry.query.filter_by(
        log_date=log_date,
        user_id=user_id
    ).all()

    return entries


def get_entry_by_id(entry_id, user_id):
    return FoodEntry.query.filter_by(
        id=entry_id,
        user_id=user_id
    ).first()


def delete_entry(entry_id, user_id):
    entry = FoodEntry.query.filter_by(
        id=entry_id,
        user_id=user_id
    ).first()

    if entry is None:
        return

    db.session.delete(entry)
    db.session.commit()


def update_entry(entry_id, log_date, food, calories, protein, carbs, fats, user_id):
    if not log_date or not food:
        return

    if None in (calories, protein, carbs, fats):
        return

    if calories < 0 or protein < 0 or carbs < 0 or fats < 0:
        return

    entry = FoodEntry.query.filter_by(
        id=entry_id,
        user_id=user_id
    ).first()

    if entry is None:
        return

    entry.log_date = log_date
    entry.food = food
    entry.calories = calories
    entry.protein = protein
    entry.carbs = carbs
    entry.fats = fats

    db.session.commit()


def set_goals(calorie_goal, protein_goal, user_id):
    if calorie_goal is None or protein_goal is None:
        return

    if calorie_goal < 0 or protein_goal < 0:
        return

    goals = Goal.query.filter_by(user_id=user_id).first()

    if goals is None:
        goals = Goal(
            calorie_goal=calorie_goal,
            protein_goal=protein_goal,
            user_id=user_id
        )

        db.session.add(goals)

    else:
        goals.calorie_goal = calorie_goal
        goals.protein_goal = protein_goal

    db.session.commit()


def get_goals(user_id):
    goals = Goal.query.filter_by(
        user_id=user_id
    ).first()

    if goals is None:
        return None

    return {
        "calorie_goal": goals.calorie_goal,
        "protein_goal": goals.protein_goal
    }