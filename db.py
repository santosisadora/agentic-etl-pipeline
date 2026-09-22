import os
import psycopg
from dotenv import load_dotenv

load_dotenv()
DB_URI = os.getenv("DATABASE_URL")

def init_db():
    """Create the table for our final, cleaned data."""
    with psycopg.connect(DB_URI) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS monster_encounters (
                    id SERIAL PRIMARY KEY,
                    monster_name TEXT,
                    threat_level INTEGER,
                    abilities TEXT[],
                    location_spotted TEXT,
                    casualties INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
        conn.commit()
        print("Database initialized successfully.")

def save_encounter(data: dict):
    """Inserts the validated dictionary into Postgres."""
    with psycopg.connect(DB_URI) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO monster_encounters (monster_name, threat_level, abilities, location_spotted, casualties)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id;
            """, (
                data['monster_name'],
                data['threat_level'],
                data['abilities'],
                data['location_spotted'],
                data.get('casualties', 0)
            ))
            new_id = cur.fetchone()[0]
        conn.commit()
        return new_id