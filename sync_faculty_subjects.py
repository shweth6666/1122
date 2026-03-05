import csv
import sqlite3
from werkzeug.security import generate_password_hash

DB_PATH = "qr_attendance.db"

def sync_data():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    try:
        if True: # Always run if file exists
            with open("faculty.csv", newline='', encoding="utf-8") as f:
                reader = csv.DictReader(f)
                faculty_count = 0
                subject_count = 0
                
                for row in reader:
                    # 1. UPSERT Faculty (Update if exists, Insert if new)
                    # We check by username
                    cur.execute("SELECT id FROM users WHERE username=?", (row["username"],))
                    user = cur.fetchone()
                    
                    hashed_pw = generate_password_hash(row["password"])
                    
                    if user:
                        # Update existing
                        cur.execute("""
                            UPDATE users 
                            SET password = ?, name = ?, branch = ?, role = 'faculty'
                            WHERE username = ?
                        """, (hashed_pw, row["name"], row["branch"], row["username"]))
                    else:
                        # Insert new
                        cur.execute("""
                            INSERT INTO users (username, password, role, name, branch)
                            VALUES (?, ?, 'faculty', ?, ?)
                        """, (row["username"], hashed_pw, row["name"], row["branch"]))
                        faculty_count += 1

                    # 2. Add Subject if it doesn't exist
                    sub_name = row.get("subject name")
                    if sub_name:
                        # Create a unique code if not present, or just use name as code for now
                        sub_code = sub_name.replace(" ", "_").upper()
                        cur.execute("SELECT id FROM subjects WHERE name=?", (sub_name,))
                        if not cur.fetchone():
                            cur.execute("""
                                INSERT OR IGNORE INTO subjects (code, name, branch, semester)
                                VALUES (?, ?, ?, ?)
                            """, (sub_code, sub_name, row["branch"], "S6")) # Defaulting to S6 as per student csv
                            subject_count += 1
            
            conn.commit()
            print("Sync Complete!")
            print("Faculty added/updated.")
            print(f"{subject_count} New Subjects created.")
            
    except Exception as e:
        print(f"Error during sync: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    sync_data()
