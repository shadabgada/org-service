import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

import random
from faker import Faker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.org_chart import OrgChart
from app.models.employee import Employee
from app.core.config import settings

fake = Faker()


def seed_database():
    engine = create_engine(settings.DATABASE_URL)
    Session = sessionmaker(bind=engine)
    db = Session()

    print("Seeding database with 10,000 org charts...")

    for org_num in range(1, 10001):
        if org_num % 1000 == 0:
            print(f"Created {org_num} org charts so far...")

        org = OrgChart(name=f"Organization {org_num}")
        db.add(org)
        db.commit()

        # Create CEO (only employee with manager_id=None)
        ceo = Employee(
            org_id=org.id,
            name=fake.name(),
            title="CEO",
            manager_id=None
        )
        db.add(ceo)
        db.commit()

        # Create other employees (4-14 employees per org)
        num_employees = random.randint(4, 14)
        employees = [ceo]  # Start with CEO as the first manager option

        # Ensure we always pick an existing employee as manager
        manager = random.choice(employees)
        for _ in range(num_employees):
            employee = Employee(
                org_id=org.id,
                name=fake.name(),
                title=fake.job(),
                manager_id=manager.id  # Guaranteed to have a manager
            )
            db.add(employee)
            employees.append(employee)  # New employee can now be a manager too

        db.commit()

    db.close()
    print("Database seeding completed!")


if __name__ == "__main__":
    seed_database()
