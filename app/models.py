from app.extensions import db


class FoodEntry(db.Model):
    __tablename__ = "log"

    id = db.Column(db.Integer, primary_key=True)
    log_date = db.Column(db.String(50), nullable=False)
    food = db.Column(db.String(100), nullable=False)
    calories = db.Column(db.Float, nullable=False)
    protein = db.Column(db.Float, nullable=False)
    carbs = db.Column(db.Float, nullable=False)
    fats = db.Column(db.Float, nullable=False)


class Goal(db.Model):
    __tablename__ = "goals"

    id = db.Column(db.Integer, primary_key=True)
    calorie_goal = db.Column(db.Float, nullable=False)
    protein_goal = db.Column(db.Float, nullable=False)