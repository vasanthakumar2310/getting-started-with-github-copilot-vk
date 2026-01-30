"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestGetActivities:
    """Test cases for fetching activities"""

    def test_get_activities_returns_dict(self):
        """Test that GET /activities returns a dictionary of activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, dict)

    def test_get_activities_has_expected_fields(self):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, details in activities.items():
            assert "description" in details
            assert "schedule" in details
            assert "max_participants" in details
            assert "participants" in details
            assert isinstance(details["participants"], list)

    def test_get_activities_contains_known_activities(self):
        """Test that known activities are in the response"""
        response = client.get("/activities")
        activities = response.json()
        
        expected_activities = ["Chess Club", "Basketball", "Tennis Club", "Art Studio"]
        for activity in expected_activities:
            assert activity in activities


class TestSignup:
    """Test cases for signing up for activities"""

    def test_signup_new_participant(self):
        """Test successfully signing up a new participant"""
        response = client.post("/activities/Chess%20Club/signup?email=test@example.com")
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]

    def test_signup_duplicate_participant_fails(self):
        """Test that signing up twice fails"""
        email = "duplicate@example.com"
        # First signup should succeed
        response1 = client.post(f"/activities/Tennis%20Club/signup?email={email}")
        assert response1.status_code == 200
        
        # Second signup should fail
        response2 = client.post(f"/activities/Tennis%20Club/signup?email={email}")
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]

    def test_signup_nonexistent_activity_fails(self):
        """Test that signing up for a nonexistent activity fails"""
        response = client.post("/activities/Nonexistent%20Activity/signup?email=test@example.com")
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_adds_participant_to_list(self):
        """Test that a participant is added to the participants list"""
        email = "newperson@example.com"
        activity_name = "Programming%20Class"
        
        # Get initial count
        response1 = client.get("/activities")
        initial_count = len(response1.json()["Programming Class"]["participants"])
        
        # Sign up
        client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Verify count increased
        response2 = client.get("/activities")
        new_count = len(response2.json()["Programming Class"]["participants"])
        assert new_count == initial_count + 1


class TestUnregister:
    """Test cases for unregistering from activities"""

    def test_unregister_existing_participant(self):
        """Test successfully unregistering an existing participant"""
        # First, sign up
        email = "unregister@example.com"
        activity_name = "Music%20Band"
        client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Then unregister
        response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]

    def test_unregister_nonexistent_participant_fails(self):
        """Test that unregistering a non-registered participant fails"""
        response = client.delete("/activities/Chess%20Club/unregister?email=notregistered@example.com")
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]

    def test_unregister_nonexistent_activity_fails(self):
        """Test that unregistering from a nonexistent activity fails"""
        response = client.delete("/activities/Nonexistent%20Activity/unregister?email=test@example.com")
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_unregister_removes_participant_from_list(self):
        """Test that a participant is removed from the participants list"""
        email = "remove@example.com"
        activity_name = "Debate%20Club"
        
        # Sign up
        client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Get count before unregister
        response1 = client.get("/activities")
        count_before = len(response1.json()["Debate Club"]["participants"])
        
        # Unregister
        client.delete(f"/activities/{activity_name}/unregister?email={email}")
        
        # Verify count decreased
        response2 = client.get("/activities")
        count_after = len(response2.json()["Debate Club"]["participants"])
        assert count_after == count_before - 1

    def test_unregister_removes_specific_participant(self):
        """Test that the correct participant is removed"""
        email1 = "person1@example.com"
        email2 = "person2@example.com"
        activity_name = "Science%20Club"
        
        # Sign up both
        client.post(f"/activities/{activity_name}/signup?email={email1}")
        client.post(f"/activities/{activity_name}/signup?email={email2}")
        
        # Unregister first person
        client.delete(f"/activities/{activity_name}/unregister?email={email1}")
        
        # Verify second person is still there
        response = client.get("/activities")
        participants = response.json()["Science Club"]["participants"]
        assert email2 in participants
        assert email1 not in participants


class TestRootRedirect:
    """Test cases for root endpoint"""

    def test_root_redirects_to_static(self):
        """Test that root endpoint redirects to index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "static/index.html" in response.headers["location"]
