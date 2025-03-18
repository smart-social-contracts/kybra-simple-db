"""Example script showing entity relationships with properties."""

import logging

from kybra_simple_db import *

# Set up audit storage
db_audit = MemoryStorage()
db = Database(db_audit=db_audit)
Database._instance = db


class User(Entity, TimestampedMixin):
    """User entity that can belong to departments and own projects."""

    name = String(min_length=2, max_length=50)
    role = String(min_length=2, max_length=50)
    # Define relationships
    departments = ManyToMany("Department", "employees")  # departments user works in
    projects = ManyToMany("Project", "team_members")  # projects user works on


class Department(Entity):
    """Department entity that has employees and manages projects."""

    name = String(min_length=2, max_length=50)
    # Define relationships
    employees = ManyToMany("User", "departments")  # employees in department
    projects = ManyToMany("Project", "departments")  # projects managed by department


class Project(Entity, TimestampedMixin):
    """Project entity that belongs to departments and has team members."""

    name = String(min_length=2, max_length=100)
    description = String(min_length=2, max_length=100)
    status = String(min_length=2, max_length=50)
    # Define relationships
    team_members = ManyToMany("User", "projects")  # team members working on project
    departments = ManyToMany("Department", "projects")  # departments managing project


# Create some users with manual IDs
alice = User(_id="user_001", name="Alice", role="Developer")
bob = User(_id="user_002", name="Bob", role="Manager")
charlie = User(_id="user_003", name="Charlie", role="Designer")
print("Created users:", alice.name, bob.name, charlie.name)
print("User IDs:", alice._id, bob._id, charlie._id)

# Create departments with manual IDs
engineering = Department(_id="dept_001", name="Engineering")
design = Department(name="Design")
print("\nCreated departments:", engineering.name, design.name)

# Create projects
website = Project(name="project", description="Company Website", status="In Progress")
mobile_app = Project(name="project", description="Mobile App", status="Planning")
print("\nCreated projects:", website.name, mobile_app.name)

# Save all entities
for entity in [alice, bob, charlie, engineering, design, website, mobile_app]:
    entity._save()

# # Set up relationships
# print("\nSetting up relationships...")

# # Department <-> User relationships
# engineering.employees = [alice, bob]      # Alice and Bob work in Engineering
# design.employees = [charlie]              # Charlie works in Design

# # Project <-> Department relationships
# engineering.projects = [website, mobile_app]  # Engineering manages both projects
# design.projects = [website]                   # Design also manages Website

# # Project <-> User relationships (team members)
# website.team_members = [alice, charlie]    # Alice and Charlie work on Website
# mobile_app.team_members = [bob]            # Bob works on Mobile App

# # Query and display relationships
# print("\nQuerying relationships...")

# # Show department members
# for dept in [engineering, design]:
#     print(f"\n{dept.name} department employees:")
#     for emp in dept.employees:
#         print(f"- {emp.name} ({emp.role})")

# # Show project teams
# for proj in [website, mobile_app]:
#     print(f"\n{proj.name} team members:")
#     for member in proj.team_members:
#         # Get the first department the member works in
#         depts = member.departments
#         dept_name = depts[0].name if depts else 'No Department'
#         print(f"- {member.name} from {dept_name}")

# # Show Alice's projects
# print(f"\n{alice.name}'s projects:")
# for proj in alice.projects:
#     print(f"- {proj.name} (Status: {proj.status})")

# # Show departments managing the website
# print(f"\nDepartments managing {website.name}:")
# for dept in website.departments:
#     print(f"- {dept.name}")

# # Show validation in action
# print("\nTrying invalid values...")
# try:
#     alice.name = "A"  # Too short
# except ValueError as e:
#     print(f"Error: {e}")

# try:
#     website.status = 123  # Wrong type
# except TypeError as e:
#     print(f"Error: {e}")

# # Test inheritance support
# print("\nTesting inheritance support...")

# class Animal(Entity, TimestampedMixin):
#     name = String(min_length=2, max_length=50)

# class Dog(Animal):
#     pass

# class Cat(Animal):
#     pass

# # Create instances
# animal_a = Animal(name="Alice")
# dog_b = Dog(name="Bob")
# cat_c = Cat(name="Charlie")

# # Save instances
# for entity in [animal_a, dog_b, cat_c]:
#     entity.save()

# # Query instances
# all_animals = Animal.instances()
# print("\nAll animals:")
# for animal in all_animals:
#     print(f"- {animal._type}: {animal.name}")

# dogs = Dog.instances()
# print("\nDogs only:")
# for dog in dogs:
#     print(f"- {dog._type}: {dog.name}")

# cats = Cat.instances()
# print("\nCats only:")
# for cat in cats:
#     print(f"- {cat._type}: {cat.name}")

# # Clean up
# for entity in [animal_a, dog_b, cat_c]:
#     entity.delete()

# # Print audit log
# print("\nAudit log:")
# for key in sorted(db_audit.keys()):
#     if key not in ['_min_id', '_max_id']:
#         print(json.loads(db_audit.get(key)))
# print("\nDatabase dump:")
# print(Database.get_instance().dump_json(pretty=True))

# # Print storage contents
# print("\nStorage contents:")
# print(db.raw_dump_json(pretty=True))

# _id = animal_a._id
# print('_id', _id)

# animal_a = Animal.load(_id)
# print('animal_a', animal_a.to_dict())

# animal_a = Animal[_id]
# print('animal_a', animal_a.to_dict())
