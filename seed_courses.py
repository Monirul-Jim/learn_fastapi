from faker import Faker
from app.database import SessionLocal
from app import models
import random

fake = Faker()

def seed_courses(total=100_000):
    db = SessionLocal()

    data = [
        {
            "name": fake.catch_phrase(),
            "instructor": fake.name(),
            "duration": round(random.uniform(1.0, 120.0), 2),
            "website": fake.url(),
        }
        for _ in range(total)
    ]

    db.bulk_insert_mappings(models.Course, data)
    db.commit()
    db.close()

    print(f"✅ Inserted {total} records")

if __name__ == "__main__":
    seed_courses()
