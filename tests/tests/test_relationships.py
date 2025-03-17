"""Tests for relationship properties in Kybra Simple DB."""

import unittest

from kybra_simple_db import *


class Person(Entity):
    """Test person entity with one-to-one relationship to profile."""

    name = String()
    profile = OneToOne(["profile"], "person")  # One-to-one with Profile


class Profile(Entity):
    """Test profile entity with one-to-one relationship to person."""

    bio = String()
    person = OneToOne(["person"], "profile")  # One-to-one with Person


class Department(Entity):
    """Test department entity with one-to-many relationship to employees."""

    name = String()
    employees = OneToMany(["employee"], "department")  # One-to-many with Employee
    manager = OneToOne(
        ["employee"], "managed_department"
    )  # One-to-one with Employee (manager)


class Employee(Entity):
    """Test employee entity."""

    name = String()
    department = ManyToOne("department")  # Many-to-one with Department
    managed_department = OneToOne(
        ["department"], "manager"
    )  # One-to-one with Department (as manager)  # Reference to parent department


class Student(Entity):
    """Test student entity with many-to-many relationship to courses."""

    name = String()
    courses = ManyToMany(["course"], "students")


class Course(Entity):
    """Test course entity with many-to-many relationship to students."""

    _entity_type = "course"

    name = String()
    students = ManyToMany(["student"], "courses")


class TestRelationships(unittest.TestCase):
    """Test cases for relationship properties."""

    def setUp(self):
        """Set up test database."""
        db_storage = MemoryStorage()
        self.db = Database(db_storage)
        Database._instance = self.db

    def test_one_to_one(self):
        """Test one-to-one relationships."""
        # Create person and profile
        person = Person(name="Alice")
        profile = Profile(bio="Software Engineer")

        # Link person and profile
        person.profile = profile

        # Verify relationships
        self.assertEqual(person.profile, profile)
        self.assertEqual(profile.person, person)

        # Verify that we can't assign multiple profiles
        profile2 = Profile(bio="Another bio")
        with self.assertRaises(ValueError):
            person.profile = [profile, profile2]

        # Test replacing profile
        new_profile = Profile(bio="Updated bio")
        person.profile = new_profile

        # Verify that old profile is unlinked and new profile is linked
        self.assertEqual(person.profile, new_profile)
        self.assertEqual(new_profile.person, person)
        self.assertIsNone(profile.person)

        # Test department manager one-to-one relationship
        dept = Department(name="Engineering")
        emp = Employee(name="Bob")

        dept.manager = emp
        self.assertEqual(dept.manager, emp)
        self.assertEqual(emp.managed_department, dept)

    def test_one_to_many(self):
        """Test one-to-many relationships."""
        # Create a department and employees
        dept = Department(name="Engineering")

        emp1 = Employee(name="Alice")
        emp2 = Employee(name="Bob")
        emp3 = Employee(name="Charlie")

        # Add employees to department
        dept.employees = [emp1, emp2]

        # Verify relationships
        self.assertEqual(len(dept.employees), 2)
        self.assertEqual(emp1.department, dept)
        self.assertEqual(emp2.department, dept)

        # Verify that we can't assign multiple departments
        dept2 = Department(name="Sales")
        with self.assertRaises(ValueError):
            emp1.department = [dept, dept2]

        # Add another employee
        dept.employees = [emp1, emp2, emp3]

        # Verify relationships
        self.assertEqual(len(dept.employees), 3)
        self.assertEqual(emp3.department, dept)

        # Move employee to new department
        dept2.employees = [emp1]

        # Verify relationships
        self.assertEqual(len(dept.employees), 2)
        self.assertEqual(len(dept2.employees), 1)
        self.assertEqual(emp1.department, dept2)

        # Test that employee can't be in multiple departments
        with self.assertRaises(ValueError):
            emp1.department = [dept, dept2]

    def test_many_to_many(self):
        """Test many-to-many relationships."""
        # Create students
        student1 = Student(name="Alice")
        student2 = Student(name="Bob")

        # Create courses
        course1 = Course(name="Math")
        course2 = Course(name="Physics")
        course3 = Course(name="Chemistry")

        # Add courses to students
        student1.courses = [course1, course2]
        student2.courses = [course2, course3]

        # Verify relationships from both sides
        self.assertEqual(len(student1.courses), 2)
        self.assertEqual(len(student2.courses), 2)
        self.assertEqual(len(course1.students), 1)
        self.assertEqual(len(course2.students), 2)
        self.assertEqual(len(course3.students), 1)

        # Remove a course from student
        student1.courses = [course1]

        # Verify relationships are updated on both sides
        self.assertEqual(len(student1.courses), 1)
        self.assertEqual(len(course2.students), 1)
        self.assertTrue(course1 in student1.courses)
        self.assertTrue(student1 in course1.students)
        self.assertFalse(student1 in course2.students)

        # Add student to multiple courses at once
        student1.courses = [course1, course2, course3]

        # Verify all relationships are updated
        self.assertEqual(len(student1.courses), 3)
        self.assertEqual(len(course2.students), 2)
        self.assertEqual(len(course3.students), 2)
        for course in [course1, course2, course3]:
            self.assertTrue(course in student1.courses)
            self.assertTrue(student1 in course.students)


if __name__ == "__main__":
    unittest.main()
