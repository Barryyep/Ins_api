from fastapi import FastAPI, HTTPException, Query
from dotenv import load_dotenv
from typing import List, Dict
import os
import requests
from pydantic import BaseModel
from datetime import datetime, timedelta
import time

load_dotenv()

app = FastAPI()

# Retrieve credentials from environment variables
APP_ID = os.getenv("APP_ID")
APP_SECRET = os.getenv("APP_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_LONG_LIVED_TOKEN")
INSTAGRAM_ACCOUNT_ID = os.getenv("INSTAGRAM_ACCOUNT_ID")


class InsightData(BaseModel):
    name: str
    period: str
    values: List[dict]
    title: str
    description: str
    id: str


class AccountInsightsResponse(BaseModel):
    data: List[InsightData]


class PostEngagement(BaseModel):
    id: str
    permalink: str
    caption: str
    like_count: int
    comments_count: int
    engagement_score: float


class TopPostsResponse(BaseModel):
    top_posts: List[PostEngagement]


class GrowthTrend(BaseModel):
    metric: str
    current_value: float
    previous_value: float
    growth_rate: float


class GrowthTrendsResponse(BaseModel):
    trends: List[GrowthTrend]


@app.get("/")
async def root():
    return {"message": "Instagram Insights API Integration"}


@app.get("/account-insights", response_model=AccountInsightsResponse)
async def get_account_insights(
    period: str = Query(
        "day", description="Time period for metrics", enum=["day", "week", "days_28"]
    ),
    metrics: str = Query(
        "impressions,reach,profile_views,website_clicks,email_contacts,get_directions_clicks,phone_call_clicks,text_message_clicks,follower_count",
        description="Comma-separated list of metrics to retrieve",
    ),
    since: str = None,
    until: str = None,
):
    """
    Retrieve Instagram account insights for the specified period and metrics.

    This endpoint fetches various performance metrics for th account.
    can specify the time period and the metrics.

    Parameters:
    - period (str): The time period for which to retrieve metrics.
                    Options are "day", "week", or "days_28". Default is "day".
    - metrics (str): Comma-separated list of metrics to retrieve.
                     Default is "impressions,reach,profile_views".
                     Available metrics include:
                     - impressions: Total number of times the IG User's IG Media have been viewed. Includes ad activity generated through the API, Facebook ads interfaces, and the Promote feature. Does not include profile views. Compatitble with day, week, days_28
                     - reach: Total number of unique users who have viewed at least one of the IG User's IG Media. Repeat views and views across different IG Media owned by the IG User by the same user are only counted as a single view. Includes ad activity generated through the API, Facebook ads interfaces, and the Promote feature. Compatitble with day, week, days_28
                     - profile_views: Number of times the profile has been viewed. Compatitble with day
                     - website_clicks: Number of taps on the website link in the profile. Compatitble with day
                     - email_contacts: Total number of taps on the email link in the IG User's profile. Compatitble with day
                     - get_directions_clicks: Number of taps on the "Get Directions" button in the profile. Compatitble with day
                     - phone_call_clicks: Number of taps on the call button in the profile. Compatitble with day
                     - text_message_clicks: Number of taps on the text message button in the profile. Compatitble with day
                     - follower_count: Total number of new followers each day within the specified range. Returns a maximum of 30 days worth of data. Not available on IG Users with fewer than 100 followers. Compatitble with day
                     - online_followers: Number of followers who were online at the time of the request. Compatitble with lifetime
    - since(str, optional): The start date for the range of data to retrieve. The value should be in Unix timestamps
    - until(str, optional): The end date for the range of data to retrieve. The value should be in Unix timestamps


    Returns:
    - AccountInsightsResponse: A Pydantic model containing the list of insights data.
      Each insight includes:
      - name: The name of the metric
      - period: The time period of the data
      - values: A list of data points, each containing a value and end_time
      - title: A human-readable title for the metric
      - description: A description of what the metric represents
      - id: A unique identifier for the insight

    Raises:
    - HTTPException: If the API request fails, with the status code and error details from Instagram's API.

    Note:
    - For more information on metrics and periods, see the Instagram Graph API documentation:
    https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/reference/ig-user/insights/#metrics-and-periods
    """
    url = f"https://graph.facebook.com/v20.0/{INSTAGRAM_ACCOUNT_ID}/insights"
    params = {"metric": metrics, "period": period, "access_token": ACCESS_TOKEN}

    if since:
        params["since"] = since
    if until:
        params["until"] = until

    try:
        data = make_api_call(url, params)
        return AccountInsightsResponse(data=data["data"])
    except HTTPException as http_exception:
        # Re-raise the HTTPException to be handled by FastAPI
        raise http_exception


@app.get("/growth-trends", response_model=GrowthTrendsResponse)
async def get_growth_trends(
    period: str = Query(
        "30d", description="Time period for growth calculation", pattern="^(\d+d)$"
    )
):
    """
    Calculate and return growth trends for the Instagram account.
    This endpoint calculates follower growth rate and engagement rate changes
    over the specified time period.
    """
    days = int(period[:-1])
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    mid_date = start_date + timedelta(days=days // 2)

    try:
        current_data = fetch_account_data(mid_date, end_date)
        previous_data = fetch_account_data(start_date, mid_date)

        follower_growth = calculate_growth(
            current_data["follower_count"],
            previous_data["follower_count"],
            "Follower Growth Rate",
        )
        engagement_growth = calculate_growth(
            current_data["engagement_rate"],
            previous_data["engagement_rate"],
            "Engagement Rate Change",
        )

        trends = [follower_growth, engagement_growth]
        return GrowthTrendsResponse(trends=trends)
    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@app.get("/top-posts", response_model=TopPostsResponse)
async def get_top_posts(
    limit: int = Query(5, description="Number of top posts to retrieve", ge=1, le=50),
    time_range: str = Query(
        "7d", description="Time range for posts", pattern="^(\d+d)$"
    ),
):
    """
    Retrieve top-performing posts based on engagement metrics.

    This endpoint fetches recent posts and sorts them based on engagement rate.

    Parameters:
    - limit (int): Number of top posts to retrieve. Default is 5, max is 50.
    - time_range (str): Time range for posts, e.g., "7d" for last 7 days. Must be in format "Xd" where X is number of days.

    Returns:
    - TopPostsResponse: A Pydantic model containing a list of top posts with their engagement metrics.
    """
    # Convert time_range to seconds
    days = int(time_range[:-1])
    since_timestamp = int(time.time()) - (days * 24 * 60 * 60)

    # Fetch recent posts
    posts = fetch_recent_posts(since_timestamp)

    # Get engagement data for each post
    posts_with_engagement = []
    for post in posts:
        engagement_data = get_post_engagement(post["id"])
        engagement_score = calculate_engagement_score(
            engagement_data, post["media_type"]
        )
        posts_with_engagement.append(
            {
                "id": post["id"],
                "permalink": post["permalink"],
                "caption": post.get("caption", ""),
                "like_count": engagement_data["like_count"],
                "comments_count": engagement_data["comments_count"],
                "engagement_score": engagement_score,
            }
        )

    # Sort posts by engagement rate and get top ones
    top_posts = sorted(
        posts_with_engagement, key=lambda x: x["engagement_score"], reverse=True
    )[:limit]

    return TopPostsResponse(top_posts=top_posts)


def make_api_call(url, params, max_retries=3, initial_backoff=5):
    retries = 0
    while retries < max_retries:
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as http_err:
            if response.status_code == 429:  # Rate limit exceeded
                retry_after = int(response.headers.get("Retry-After", initial_backoff))
                if retries < max_retries - 1:
                    print(f"Rate limit exceeded. Retrying after {retry_after} seconds.")
                    time.sleep(retry_after)
                    retries += 1
                else:
                    raise HTTPException(
                        status_code=429,
                        detail="Rate limit exceeded. Please try again later.",
                    )
            else:
                error_detail = (
                    response.json().get("error", {}).get("message", str(http_err))
                )
                raise HTTPException(
                    status_code=response.status_code, detail=error_detail
                )
        except requests.RequestException as req_err:
            raise HTTPException(
                status_code=500, detail=f"Request failed: {str(req_err)}"
            )
        except ValueError as json_err:
            raise HTTPException(
                status_code=500, detail=f"Invalid JSON response: {str(json_err)}"
            )

    raise HTTPException(
        status_code=429, detail="Rate limit exceeded. Please try again later."
    )


def fetch_recent_posts(since_timestamp):
    url = f"https://graph.facebook.com/v20.0/{INSTAGRAM_ACCOUNT_ID}/media"
    params = {
        "fields": "id,caption,media_type,permalink,timestamp",
        "access_token": ACCESS_TOKEN,
        "since": since_timestamp,
    }
    try:
        response_data = make_api_call(url, params)
        return response_data["data"]
    except HTTPException as http_exception:
        print(f"Error fetching recent posts: {http_exception.detail}")
        raise


def get_post_engagement(post_id):
    url = f"https://graph.facebook.com/v20.0/{post_id}"
    params = {"fields": "like_count,comments_count", "access_token": ACCESS_TOKEN}
    try:
        return make_api_call(url, params)
    except HTTPException as http_exception:
        print(
            f"Error getting post engagement for post {post_id}: {http_exception.detail}"
        )
        raise


def calculate_engagement_score(engagement_data, media_type):
    # using a simple formula for engagement score instead of rate since cannot get follower number
    total_interactions = (
        engagement_data["like_count"] + engagement_data["comments_count"]
    )
    return total_interactions


def fetch_account_data(start_date: datetime, end_date: datetime) -> Dict[str, float]:
    """Fetch account data for a given date range."""
    url = f"https://graph.facebook.com/v20.0/{INSTAGRAM_ACCOUNT_ID}/insights"
    params = {
        "metric": "follower_count,reach,impressions",
        "period": "day",
        "since": int(start_date.timestamp()),
        "until": int(end_date.timestamp()),
        "access_token": ACCESS_TOKEN,
    }

    try:
        data = make_api_call(url, params)["data"]
        follower_count = sum(
            point["values"][0]["value"]
            for point in data
            if point["name"] == "follower_count"
        )
        reach = sum(
            point["values"][0]["value"] for point in data if point["name"] == "reach"
        )
        impressions = sum(
            point["values"][0]["value"]
            for point in data
            if point["name"] == "impressions"
        )

        # Calculate engagement rate (impressions / reach)
        engagement_rate = impressions / reach if reach > 0 else 0

        return {"follower_count": follower_count, "engagement_rate": engagement_rate}
    except HTTPException as http_err:
        raise http_err


def calculate_growth(
    current_value: float, previous_value: float, metric_name: str
) -> GrowthTrend:
    """Calculate growth rate between two values."""
    if previous_value > 0:
        growth_rate = ((current_value - previous_value) / previous_value) * 100
    else:
        growth_rate = 100 if current_value > 0 else 0

    return GrowthTrend(
        metric=metric_name,
        current_value=current_value,
        previous_value=previous_value,
        growth_rate=growth_rate,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
