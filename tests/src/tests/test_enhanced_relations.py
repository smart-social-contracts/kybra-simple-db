"""Tests for enhanced relation functionality with string ID/name resolution."""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from tester import Tester

from kybra_simple_db import *


# Test entities for comprehensive relation testing
class User(Entity, TimestampedMixin):
    __alias__ = "username"
    username = String(min_length=2, max_length=50)
    email = String(max_length=100)
    profile = OneToOne("Profile", "user")
    department = ManyToOne("Department", "employees")
    projects = ManyToMany("Project", "members")


class Profile(Entity, TimestampedMixin):
    __alias__ = "name"
    name = String(min_length=2, max_length=100)
    bio = String(max_length=500)
    user = OneToOne("User", "profile")


class Department(Entity, TimestampedMixin):
    __alias__ = "name"
    name = String(min_length=2, max_length=100)
    budget = Integer(min_value=0)
    employees = OneToMany("User", "department")


class Project(Entity, TimestampedMixin):
    __alias__ = "name"
    name = String(min_length=2, max_length=100)
    description = String(max_length=500)
    members = ManyToMany("User", "projects")


class TestEnhancedRelations:
    def setUp(self):
        """Reset Entity class variables before each test."""
        Database.get_instance().clear()

    def test_one_to_one_entity_resolution(self):
        """Test OneToOne relations with entity, ID, and name resolution."""
        user1 = User(username="alice", email="alice@example.com")
        user2 = User(username="bob", email="bob@example.com")
        profile1 = Profile(name="Alice Smith", bio="Software Engineer")
        profile2 = Profile(name="Bob Jones", bio="Product Manager")

        # Verify initial state
        assert user1.profile is None, "user1.profile should initially be None"
        assert user2.profile is None, "user2.profile should initially be None"
        assert profile1.user is None, "profile1.user should initially be None"
        assert profile2.user is None, "profile2.user should initially be None"

        # Set using entity instance
        user1.profile = profile1
        assert user1.profile == profile1, "user1.profile should be set to profile1"
        assert (
            profile1.user == user1
        ), "profile1.user should be set to user1 (reverse relation)"

        # Set using string ID
        user2.profile = profile2._id
        assert (
            user2.profile == profile2
        ), f"user2.profile should be set to profile2 using ID '{profile2._id}'"
        assert (
            profile2.user == user2
        ), "profile2.user should be set to user2 (reverse relation)"

        # Set using alias/name - should switch profile2 from user2 to user1
        profile2.user = "alice"
        assert profile2.user == user1, "profile2.user should be switched to alice"
        assert user1.profile == profile2, "user1.profile should now be profile2"
        assert user2.profile is None, "user2.profile should now be None (switched away)"

    def test_many_to_one_entity_resolution(self):
        """Test ManyToOne relations with entity, ID, and name resolution."""
        user1 = User(username="alice", email="alice@example.com")
        user2 = User(username="bob", email="bob@example.com")
        dept = Department(name="Engineering", budget=100000)

        # Verify initial state
        assert user1.department is None, "user1.department should initially be None"
        assert user2.department is None, "user2.department should initially be None"
        assert len(dept.employees) == 0, "dept.employees should initially be empty"

        # Set using entity instance
        user1.department = dept
        assert user1.department == dept, "user1.department should be set to dept"
        assert (
            user1 in dept.employees
        ), "user1 should be in dept.employees (reverse relation)"

        # Set using string ID
        user2.department = dept._id
        assert (
            user2.department == dept
        ), f"user2.department should be set to dept using ID '{dept._id}'"
        assert (
            user2 in dept.employees
        ), "user2 should be in dept.employees (reverse relation)"
        assert len(dept.employees) == 2, "dept.employees should now have 2 members"

        # Set using alias/name
        user3 = User(username="charlie", email="charlie@example.com")
        user3.department = "Engineering"
        assert (
            user3.department == dept
        ), "user3.department should be set to dept using name 'Engineering'"
        assert (
            user3 in dept.employees
        ), "user3 should be in dept.employees (reverse relation)"
        assert len(dept.employees) == 3, "dept.employees should now have 3 members"

    def test_one_to_many_entity_resolution(self):
        """Test OneToMany relations with mixed entity, ID, and name resolution."""
        user1 = User(username="alice", email="alice@example.com")
        user2 = User(username="bob", email="bob@example.com")
        user3 = User(username="charlie", email="charlie@example.com")
        user4 = User(username="diana", email="diana@example.com")
        dept = Department(name="Engineering", budget=100000)

        # Verify initial state
        assert len(dept.employees) == 0, "dept.employees should initially be empty"
        assert user1.department is None, "user1.department should initially be None"
        assert user2.department is None, "user2.department should initially be None"
        assert user3.department is None, "user3.department should initially be None"
        assert user4.department is None, "user4.department should initially be None"

        # Set using mix of entity instances and string IDs/names
        dept.employees = [user3, user4._id, "alice"]  # Mix of entity, ID, and name
        expected_usernames = {"charlie", "diana", "alice"}
        actual_usernames = {emp.username for emp in dept.employees}
        assert (
            actual_usernames == expected_usernames
        ), f"dept.employees should contain {expected_usernames}, got {actual_usernames}"

        # Verify reverse relations
        assert user3.department == dept, "user3.department should be set to dept"
        assert user4.department == dept, "user4.department should be set to dept"
        assert user1.department == dept, "user1.department should be set to dept"
        assert user2.department is None, "user2.department should still be None"

    def test_many_to_many_entity_resolution(self):
        """Test ManyToMany relations with mixed entity, ID, and name resolution."""
        user1 = User(username="alice", email="alice@example.com")
        user2 = User(username="bob", email="bob@example.com")
        user3 = User(username="charlie", email="charlie@example.com")
        project1 = Project(name="WebApp", description="Main web application")

        # Verify initial state
        assert len(project1.members) == 0, "project1.members should initially be empty"
        assert len(user1.projects) == 0, "user1.projects should initially be empty"
        assert len(user2.projects) == 0, "user2.projects should initially be empty"
        assert len(user3.projects) == 0, "user3.projects should initially be empty"

        # Set using mix of entity instances and string IDs/names
        project1.members = [user1, user2._id, "charlie"]  # Mix of entity, ID, and name
        expected_usernames = {"alice", "bob", "charlie"}
        actual_usernames = {member.username for member in project1.members}
        assert (
            actual_usernames == expected_usernames
        ), f"project1.members should contain {expected_usernames}, got {actual_usernames}"

        # Verify reverse relations
        assert project1 in user1.projects, "project1 should be in user1.projects"
        assert project1 in user2.projects, "project1 should be in user2.projects"
        assert project1 in user3.projects, "project1 should be in user3.projects"

    def test_many_to_many_single_entity_assignment(self):
        """Test ManyToMany relations with single entity assignment."""
        user1 = User(username="alice", email="alice@example.com")
        project1 = Project(name="WebApp", description="Main web application")

        # Verify initial state
        assert len(user1.projects) == 0, "user1.projects should initially be empty"
        assert len(project1.members) == 0, "project1.members should initially be empty"

        # Test single entity assignment
        user1.projects = project1
        assert (
            project1 in user1.projects
        ), "project1 should be in user1.projects after single entity assignment"
        assert (
            user1 in project1.members
        ), "user1 should be in project1.members (reverse relation)"
        assert len(user1.projects) == 1, "user1.projects should have exactly 1 project"

        # Test single entity assignment using string name
        user1.projects = "WebApp"
        assert (
            project1 in user1.projects
        ), "project1 should still be in user1.projects after string name assignment"
        assert (
            len(user1.projects) == 1
        ), "user1.projects should still have exactly 1 project"

    def test_relation_list_add_with_entity_resolution(self):
        """Test RelationList.add with entity, ID, and name resolution."""
        user1 = User(username="alice", email="alice@example.com")
        user2 = User(username="bob", email="bob@example.com")
        project1 = Project(name="WebApp", description="Main web application")

        # Verify initial state
        assert len(project1.members) == 0, "project1.members should initially be empty"

        # Add using string ID
        project1.members.add(user1._id)
        assert (
            user1 in project1.members
        ), f"user1 should be in project1.members after adding by ID '{user1._id}'"
        assert (
            project1 in user1.projects
        ), "project1 should be in user1.projects (reverse relation)"
        assert len(project1.members) == 1, "project1.members should have 1 member"

        # Add using alias/name
        project1.members.add("bob")
        assert (
            user2 in project1.members
        ), "user2 should be in project1.members after adding by alias 'bob'"
        assert (
            project1 in user2.projects
        ), "project1 should be in user2.projects (reverse relation)"
        expected_usernames = {"alice", "bob"}
        actual_usernames = {m.username for m in project1.members}
        assert (
            actual_usernames == expected_usernames
        ), f"project1.members should contain {expected_usernames}, got {actual_usernames}"

    def test_invalid_entity_resolution(self):
        """Test error handling for invalid entity resolution."""
        user1 = User(username="alice", email="alice@example.com")
        project1 = Project(name="WebApp", description="Main web application")

        # Test invalid ID
        try:
            user1.projects = "nonexistent_id"
            assert False, "Should have raised ValueError for nonexistent ID"
        except ValueError as e:
            assert "No entity of types" in str(
                e
            ), f"Expected 'No entity of types' in error message, got: {str(e)}"

        # Test invalid type
        try:
            user1.projects = 123.45  # float is not supported
            assert False, "Should have raised TypeError for invalid type"
        except TypeError as e:
            assert "must be set to an entity or list of entities" in str(
                e
            ), f"Expected type error message, got: {str(e)}"

    def test_mixed_relation_scenarios(self):
        """Test complex scenarios with mixed relation types and entity resolution."""
        # Create entities
        user1 = User(username="alice", email="alice@example.com")
        user2 = User(username="bob", email="bob@example.com")
        profile1 = Profile(name="Alice Smith", bio="Software Engineer")
        dept = Department(name="Engineering", budget=100000)
        project1 = Project(name="WebApp", description="Main web application")
        project2 = Project(name="MobileApp", description="Mobile companion app")

        # Set up complex relationships using mixed resolution methods
        user1.profile = profile1._id  # OneToOne using ID
        user1.department = "Engineering"  # ManyToOne using name
        user1.projects = [project1, project2._id]  # ManyToMany using mixed types

        # Verify all relationships
        assert user1.profile == profile1, "OneToOne relationship should be established"
        assert (
            profile1.user == user1
        ), "OneToOne reverse relationship should be established"
        assert user1.department == dept, "ManyToOne relationship should be established"
        assert (
            user1 in dept.employees
        ), "ManyToOne reverse relationship should be established"
        assert (
            project1 in user1.projects
        ), "ManyToMany relationship with project1 should be established"
        assert (
            project2 in user1.projects
        ), "ManyToMany relationship with project2 should be established"
        assert (
            user1 in project1.members
        ), "ManyToMany reverse relationship with project1 should be established"
        assert (
            user1 in project2.members
        ), "ManyToMany reverse relationship with project2 should be established"


def run(test_name: str = None, test_var: str = None):
    """Run all enhanced relation tests."""
    tester = Tester(TestEnhancedRelations)
    return tester.run_tests()


if __name__ == "__main__":
    exit(run())
