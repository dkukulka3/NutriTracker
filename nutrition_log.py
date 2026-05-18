#Daily nutrition tracker program
#Importing sqlite and setting file name
import sqlite3
DB_PATH = "nutrition_log.db"

# Init function to setup program
def init_db():
    with sqlite3.connect(DB_PATH) as connection:
        c = connection.cursor()

        # Nutrient log table
        c.execute("""
            CREATE TABLE IF NOT EXISTS log (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  log_date TEXT,
                  food TEXT,
                  calories REAL,
                  protein REAL,
                  carbs REAL,
                  fats REAL
                  )
              """)

        # Protein/calories goal table
        c.execute("""
            CREATE TABLE IF NOT EXISTS goals (
                  id INTEGER PRIMARY KEY,
                  calorie_goal REAL,
                  protein_goal REAL
                  )
              """)


# Function to add entries
def add_entry(log_date, food, calories, protein, carbs, fats):
    # Backend validation
    if not log_date or not food:
        return

    if None in (calories, protein, carbs, fats):
        return

    if calories < 0 or protein < 0 or carbs < 0 or fats < 0:
        return

    with sqlite3.connect(DB_PATH) as connection:
        c = connection.cursor()

        c.execute("""
            INSERT INTO log (log_date, food, calories, protein, carbs, fats)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (log_date, food, calories, protein, carbs, fats))


# Function to calculate totals
def calculate_total(log_date):
    with sqlite3.connect(DB_PATH) as connection:
        c = connection.cursor()

        c.execute("""
                  SELECT SUM(calories), SUM(protein), SUM(carbs), SUM(fats)
                  FROM log
                  WHERE log_date = ?
                  """, (log_date,))

        # Create tuple
        row = c.fetchone()

    # Assign each position of the tuple to a variable
    total_calories, total_protein, total_carbs, total_fats = [
        value or 0 for value in row
    ]

    return {
        "calories": total_calories,
        "protein": total_protein,
        "carbs": total_carbs,
        "fats": total_fats
    }


# Function to set protein/calorie goals
def set_goals(calorie_goal, protein_goal):
    # Backend validation
    if calorie_goal is None or protein_goal is None:
        return

    if calorie_goal < 0 or protein_goal < 0:
        return

    with sqlite3.connect(DB_PATH) as connection:
        c = connection.cursor()

        c.execute("""
            INSERT OR REPLACE INTO goals (id, calorie_goal, protein_goal)
            VALUES (1, ?, ?)
        """, (calorie_goal, protein_goal))


# Function to load goal data
def get_goals():
    with sqlite3.connect(DB_PATH) as connection:
        c = connection.cursor()

        c.execute("""
            SELECT calorie_goal, protein_goal
            FROM goals
            WHERE id = 1
        """)

        row = c.fetchone()

    if row is None:
        return None

    return {
        "calorie_goal": row[0],
        "protein_goal": row[1]
    }


#Function to display food entries for a given day
def get_entries_by_date(log_date):
    with sqlite3.connect(DB_PATH) as connection:
        c = connection.cursor()

        c.execute("""
            SELECT id, food, calories, protein, carbs, fats
            FROM log
            WHERE log_date = ?
        """, (log_date,))   
        rows = c.fetchall()
        return rows
                  
                  # Function to delete a food entry
def delete_entry(entry_id):
    with sqlite3.connect(DB_PATH) as connection:
        c = connection.cursor()

        c.execute("""
            DELETE FROM log
            WHERE id = ?
        """, (entry_id,))
                  
# Function to get one food entry by ID
def get_entry_by_id(entry_id):
    with sqlite3.connect(DB_PATH) as connection:
        c = connection.cursor()

        c.execute("""
            SELECT id, log_date, food, calories, protein, carbs, fats
            FROM log
            WHERE id = ?
        """, (entry_id,))

        row = c.fetchone()
        return row

# Function to update/edit a food entry
def update_entry(entry_id, log_date, food, calories, protein, carbs, fats):
    # Backend validation
    if not log_date or not food:
        return

    if None in (calories, protein, carbs, fats):
        return

    if calories < 0 or protein < 0 or carbs < 0 or fats < 0:
        return

    with sqlite3.connect(DB_PATH) as connection:
        c = connection.cursor()

        c.execute("""
            UPDATE log
            SET log_date = ?,
                food = ?,
                calories = ?,
                protein = ?,
                carbs = ?,
                fats = ?
            WHERE id = ?
        """, (log_date, food, calories, protein, carbs, fats, entry_id))

# Main menu function
def main():
    init_db()
    #Variable that stores current date
    current_log_date = None
    while True:
        print("\nNutrition Tracker")
        print("1. Create new entry")
        print("2. Add a food")
        print("3. Calculate daily totals")        
        print("4. Set calorie and protein goals")
        print("5. Exit")

        choice = input("Choose an option (1-5): ")

        if choice == "1":
            current_log_date = input("Enter log date (YYYY-MM-DD): ")
            print("Current log date set to:", current_log_date)

        elif choice == "2":
            if current_log_date is None:
                print("Please create/select a log date first.")
            else:
                food = input("Enter food name: ")
                calories = float(input("Enter calories: "))
                protein = float(input("Enter protein: "))
                carbs = float(input("Enter carbs: "))
                fats = float(input("Enter fats: "))
                add_entry(current_log_date, food, calories, protein, carbs, fats)
                print("Food added successfully and saved.")

        elif choice == "3":
            if current_log_date is None:
                print("Please create a new log entry first.")
            else:
                totals = calculate_total(current_log_date)
                goals = get_goals()
                print("\nDaily Totals:")
                print("Calories:", totals["calories"])
                print("Protein:", totals["protein"])            
                print("Carbs:", totals["carbs"])
                print("Fats:", totals["fats"])
                if goals is None:
                    print("\nNo goals set yet.")
                else:
                    print("\nGoal Progress:")
                    cal_goal = goals["calorie_goal"]
                    prot_goal = goals["protein_goal"]

                    cal_diff = cal_goal - totals["calories"]
                    prot_diff = prot_goal - totals["protein"]

                    print(f"Calories: {totals['calories']} / {cal_goal}")
                    print(f"Protein: {totals['protein']} / {prot_goal}")

                    print("Remaining Calories:", cal_diff)
                    print("Remaining Protein:", prot_diff)

        elif choice == "4":
            calorie_goal = float(input("Enter calorie goal: "))
            protein_goal = float(input("Enter protein goal: "))
            set_goals(calorie_goal, protein_goal)
            print("Goals saved successfully.")
                    
        elif choice == "5":
            print("Exiting program.")
            break

        else:
            print("Invalid choice. Please select 1-5.")


if __name__ == "__main__":
    main()