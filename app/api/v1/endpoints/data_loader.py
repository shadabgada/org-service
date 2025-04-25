from fastapi import APIRouter

from scripts.seed_db import seed_database

router = APIRouter()


@router.get("/populate")
def seed_data():
    print("Starting seed process...")
    try:
        seed_database()
        return {"message": "Seeding completed successfully!"}
    except Exception as e:
        print(f"Error during seeding: {e}")
        return {"error": f"Seeding failed: {str(e)}"}
