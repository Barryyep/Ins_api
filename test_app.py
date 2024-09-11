import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from app import app

client = TestClient(app)

# Mock data
mock_account_insights = {
    "data": [
        {
            "name": "impressions",
            "period": "day",
            "values": [{"value": 1000, "end_time": "2024-09-11T00:00:00+0000"}],
            "title": "Impressions",
            "description": "Total number of times the IG User's IG Media have been viewed",
            "id": "12345_impressions",
        }
    ]
}

mock_growth_data = {"follower_count": 1000, "engagement_rate": 0.05}

mock_posts = [
    {
        "id": "123",
        "permalink": "https://www.instagram.com/p/123/",
        "caption": "Test post",
        "media_type": "IMAGE",
    }
]

mock_engagement = {"like_count": 100, "comments_count": 10}

# Unit tests


def test_get_account_insights():
    with patch("app.make_api_call", return_value=mock_account_insights):
        response = client.get("/account-insights?period=day&metrics=impressions")
        assert response.status_code == 200
        assert response.json() == {"data": mock_account_insights["data"]}


def test_get_growth_trends():
    with patch(
        "app.fetch_account_data", side_effect=[mock_growth_data, mock_growth_data]
    ):
        response = client.get("/growth-trends?period=30d")
        assert response.status_code == 200
        assert "trends" in response.json()
        assert len(response.json()["trends"]) == 2


def test_get_top_posts():
    with patch("app.fetch_recent_posts", return_value=mock_posts):
        with patch("app.get_post_engagement", return_value=mock_engagement):
            response = client.get("/top-posts?limit=1&time_range=7d")
            assert response.status_code == 200
            assert "top_posts" in response.json()
            assert len(response.json()["top_posts"]) == 1


# Integration tests
def test_account_insights_integration():
    response = client.get("/account-insights?period=day&metrics=impressions,reach")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert len(data["data"]) > 0
    assert all(
        key in data["data"][0]
        for key in ["name", "period", "values", "title", "description", "id"]
    )


def test_growth_trends_integration():
    response = client.get("/growth-trends?period=30d")
    assert response.status_code == 200
    data = response.json()
    assert "trends" in data
    assert len(data["trends"]) == 2
    for trend in data["trends"]:
        assert isinstance(trend, dict)
        assert all(
            key in trend
            for key in ["metric", "current_value", "previous_value", "growth_rate"]
        )
        assert isinstance(trend["metric"], str)
        assert isinstance(trend["current_value"], (int, float))
        assert isinstance(trend["previous_value"], (int, float))
        assert isinstance(trend["growth_rate"], (int, float))

    # Check for specific metrics
    metrics = [trend["metric"] for trend in data["trends"]]
    assert "Follower Growth Rate" in metrics
    assert "Engagement Rate Change" in metrics


def test_top_posts_integration():
    response = client.get("/top-posts?limit=5&time_range=7d")
    assert response.status_code == 200
    data = response.json()
    assert "top_posts" in data
    assert len(data["top_posts"]) <= 5
    assert all(
        key in data["top_posts"][0]
        for key in [
            "id",
            "permalink",
            "caption",
            "like_count",
            "comments_count",
            "engagement_score",
        ]
    )


# Helper function tests
def test_calculate_growth():
    from app import calculate_growth, GrowthTrend

    # Test case 1: Normal growth
    result = calculate_growth(1100, 1000, "Test Growth")
    assert isinstance(result, GrowthTrend)
    assert result.metric == "Test Growth"
    assert result.current_value == 1100
    assert result.previous_value == 1000
    assert result.growth_rate == pytest.approx(10.0)

    # Test case 2: No growth
    result_no_growth = calculate_growth(1000, 1000, "No Growth")
    assert result_no_growth.growth_rate == 0

    # Test case 3: Negative growth
    result_negative = calculate_growth(900, 1000, "Negative Growth")
    assert result_negative.growth_rate == pytest.approx(-10.0)

    # Test case 4: Growth from zero
    result_from_zero = calculate_growth(100, 0, "Growth from Zero")
    assert result_from_zero.growth_rate == 100

    # Test case 5: Zero to zero
    result_zero_to_zero = calculate_growth(0, 0, "Zero to Zero")
    assert result_zero_to_zero.growth_rate == 0


def test_calculate_engagement_rate():
    from app import calculate_engagement_score

    result = calculate_engagement_score(
        {"like_count": 100, "comments_count": 10}, "IMAGE"
    )
    assert result == pytest.approx(110)  # Assuming follower count is 1000


# Error handling tests


def test_account_insights_error_handling():
    # Test case 1: HTTP error
    with patch(
        "app.make_api_call",
        side_effect=HTTPException(status_code=400, detail="Bad Request"),
    ):
        response = client.get("/account-insights?period=day&metrics=impressions")
        assert response.status_code == 400
        assert response.json() == {"detail": "Bad Request"}

    # Test case 2: Rate limit exceeded
    with patch(
        "app.make_api_call",
        side_effect=HTTPException(
            status_code=429, detail="Rate limit exceeded. Please try again later."
        ),
    ):
        response = client.get("/account-insights?period=day&metrics=impressions")
        assert response.status_code == 429
        assert response.json() == {
            "detail": "Rate limit exceeded. Please try again later."
        }

    # Test case 3: Internal server error
    with patch(
        "app.make_api_call",
        side_effect=HTTPException(status_code=500, detail="Internal Server Error"),
    ):
        response = client.get("/account-insights?period=day&metrics=impressions")
        assert response.status_code == 500
        assert response.json() == {"detail": "Internal Server Error"}

    # Test case 4: Invalid JSON response
    with patch(
        "app.make_api_call",
        side_effect=HTTPException(
            status_code=500, detail="Invalid JSON response: Invalid JSON"
        ),
    ):
        response = client.get("/account-insights?period=day&metrics=impressions")
        assert response.status_code == 500
        assert response.json() == {"detail": "Invalid JSON response: Invalid JSON"}
