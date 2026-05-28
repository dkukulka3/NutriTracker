#Daily nutrition tracker program
#Importing libraries
from app.extensions import db
from app.models import FoodEntry, Goal
from sqlalchemy import func

# Function to add entries
def add_entry(log_date, food, calories, protein, carbs, fats):
    """
    Add a new food entry to the database using SQLAlchemy.
    """

    new_entry = FoodEntry(
        log_date=log_date,
        food=food,
        calories=calories,
        protein=protein,
        carbs=carbs,
        fats=fats
    )

    db.session.add(new_entry)
    db.session.commit()


# Function to calculate totals
def calculate_total(log_date):
    """
    Calculate nutrition totals for a given date using SQLAlchemy.
    """

    totals = db.session.query(
        func.sum(FoodEntry.calories),
        func.sum(FoodEntry.protein),
        func.sum(FoodEntry.carbs),
        func.sum(FoodEntry.fats)
    ).filter(
        FoodEntry.log_date == log_date
    ).first()

    return {
        "calories": totals[0] or 0,
        "protein": totals[1] or 0,
        "carbs": totals[2] or 0,
        "fats": totals[3] or 0
    }


# Function to set protein/calorie goals
def set_goals(calorie_goal, protein_goal):
    if calorie_goal is None or protein_goal is None:
        return

    if calorie_goal < 0 or protein_goal < 0:
        return

    goals = Goal.query.get(1)

    if goals is None:
        goals = Goal(
            id=1,
            calorie_goal=calorie_goal,
            protein_goal=protein_goal
        )
        db.session.add(goals)
    else:
        goals.calorie_goal = calorie_goal
        goals.protein_goal = protein_goal

    db.session.commit()


# Function to load goal data
def get_goals():
    goals = Goal.query.get(1)

    if goals is None:
        return None

    return {
        "calorie_goal": goals.calorie_goal,
        "protein_goal": goals.protein_goal
    }


#Function to display food entries for a given day
def get_entries_by_date(log_date):
    """
    Retrieve all food entries for a given date using SQLAlchemy.
    """

    entries = FoodEntry.query.filter_by(
        log_date=log_date
    ).all()

    return entries
                  
                  # Function to delete a food entry
def delete_entry(entry_id):
    """
    Delete one food entry by ID using SQLAlchemy.
    """

    entry = FoodEntry.query.get(entry_id)

    if entry is None:
        return

    db.session.delete(entry)
    db.session.commit()
                  
# Function to get one food entry by ID
def get_entry_by_id(entry_id):
    """
    Retrieve one food entry by its ID using SQLAlchemy.
    """

    return FoodEntry.query.get(entry_id)

# Function to update/edit a food entry
def update_entry(entry_id, log_date, food, calories, protein, carbs, fats):
    if not log_date or not food:
        return

    if None in (calories, protein, carbs, fats):
        return

    if calories < 0 or protein < 0 or carbs < 0 or fats < 0:
        return

    entry = FoodEntry.query.get(entry_id)

    if entry is None:
        return

    entry.log_date = log_date
    entry.food = food
    entry.calories = calories
    entry.protein = protein
    entry.carbs = carbs
    entry.fats = fats

    db.session.commit()