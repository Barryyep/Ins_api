from fastapi import FastAPI, HTTPException, Query
from dotenv import load_dotenv
from typing import List
import os
import requests
from pydantic import BaseModel
from top_post import router as top_posts_router

load_dotenv()

app = FastAPI()
app.include_router(top_posts_router, tags=["media"])

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


@app.get("/")
async def root():
    return {"message": "Instagram Insights API Integration"}


@app.get("/account-insights", response_model=AccountInsightsResponse)
async def get_account_insights(
    period: str = Query(
        "day", description="Time period for metrics", enum=["day", "week", "days_28"]
    ),
    metrics: str = Query(
        "impressions,reach,profile_views,website_clicks,email_contacts,get_directions_clicks,phone_call_clicks,text_message_clicks,follower_count,online_followers",
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
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        return response.json()
    except requests.HTTPError as http_err:
        # Handle HTTP errors (4xx and 5xx responses)
        error_detail = response.json().get("error", {}).get("message", str(http_err))
        raise HTTPException(status_code=response.status_code, detail=error_detail)
    except requests.RequestException as req_err:
        # Handle any other requests-related errors (e.g., connection errors)
        raise HTTPException(status_code=500, detail=f"Request failed: {str(req_err)}")
    except ValueError as json_err:
        # Handle JSON decoding errors
        raise HTTPException(
            status_code=500, detail=f"Invalid JSON response: {str(json_err)}"
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
