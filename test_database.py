from database import get_connection


with get_connection() as conn:
    print("Successfully connected to Neon!")
