# Instagram Insights API Integration

# Configuration
## Table of Contents(from scratch)
1. Create Facebook Account
2. Create Facebook Page
3. Create Instagram Account
4. [Convert Instagram to Business/Creator Account](#4-convert-instagram-to-businesscreator-account)
5. [Link Instagram to Facebook Page](#5-link-instagram-to-facebook-page)
6. Create Facebook Developer Account
7. [Create Facebook App](#7-create-facebook-app)
8. [Get Facebook Page ID](#8-get-facebook-page-id)
9. [Get Instagram Account ID](#9-get-instagram-account-id)

## 4. Convert Instagram to Business/Creator Account

1. Open Instagram app
2. Go to your profile
3. Tap the hamburger menu (≡) in the top right
4. Go to Settings > Account
5. Scroll down and tap "Switch to Professional Account"
6. Choose "Business" or "Creator" based on your needs

## 5. Link Instagram to Facebook Page

1. In Instagram, go to Settings > Account > Linked Accounts
2. Tap "Facebook" and log in
3. Select the Facebook Page you want to link
4. Follow the prompts to complete the connection


## 7. Create Facebook App

1. In the Facebook Developers portal, click "Create App"
2. Choose an app type
3. Fill in the required information
4. Get the APP_SECRET and APP_ID

## 8. Get Facebook Page ID

1. Log in to [facebook business](https://business.facebook.com)
2. Look at the URL. It should be in the format: `https://business.facebook.com/latest/home?business_id=1234567&asset_id=1234567`. The asset_id is the page id

## 9. Get Instagram Account ID

Using the Facebook Graph API Explorer:

1. Go to [developers.facebook.com/tools/explorer](https://developers.facebook.com/tools/explorer)
2. Select your app from the dropdown
3. Generate a user token with `instagram_basic` and `pages_show_list`,`read_insights`,`instagram_manage_insights`,`pages_read_engagement`,`pages_read_user_content`permissions
4. In the query field, enter: `{page-id}?fields=instagram_business_account`
   Replace `{page-id}` with your actual Page ID
5. Click "Submit"
6. The response will contain the Instagram account ID in the `instagram_business_account` field

## Store the according id/token in .env
APP_ID=xxx
APP_SECRET=xxx
ACCESS_LONG_LIVED_TOKEN=xxx
INSTAGRAM_ACCOUNT_ID = xxx
PAGE_ID = xxx

Noted that the ACCESS_LONG_LIVED_TOKEN (long-lived access tokens) for the Instagram Graph API typically last for about 60 days. So need to update in every 60 days


1. pip install -r requirement.txt
2. python app.py

# Overview of the implemented endpoints and their functionalities

## API Endpoints

### Account Insights

Retrieve Instagram account insights for the specified period and metrics.

#### Endpoint

```
GET /account-insights
```

#### Query Parameters

| Parameter | Type   | Required | Description                                                   |
|-----------|--------|----------|---------------------------------------------------------------|
| period    | string | Yes      | Time period for metrics. Options: "day", "week", "days_28"    |
| metrics   | string | Yes      | Comma-separated list of metrics to retrieve                   |
| since     | string | No       | Start date for the range of data (Unix timestamp)             |
| until     | string | No       | End date for the range of data (Unix timestamp)               |

#### Available Metrics

- `impressions`: Total number of times the IG User's IG Media have been viewed
- `reach`: Total number of unique users who have viewed at least one of the IG User's IG Media
- `profile_views`: Number of times the profile has been viewed
- `website_clicks`: Number of taps on the website link in the profile
- `email_contacts`: Total number of taps on the email link in the IG User's profile
- `get_directions_clicks`: Number of taps on the "Get Directions" button in the profile
- `phone_call_clicks`: Number of taps on the call button in the profile
- `text_message_clicks`: Number of taps on the text message button in the profile
- `follower_count`: Total number of new followers each day within the specified range( only return when `follower_count`>100)

#### Example Request

```
GET /account-insights?period=day&metrics=impressions,reach&since=1630454400&until=1630540800
```

#### Example Response

```json
{
  "data": [
    {
      "name": "impressions",
      "period": "day",
      "values": [
        {
          "value": 1000,
          "end_time": "2024-09-11T00:00:00+0000"
        }
      ],
      "title": "Impressions",
      "description": "Total number of times the IG User's IG Media have been viewed",
      "id": "12345_impressions"
    },
    {
      "name": "reach",
      "period": "day",
      "values": [
        {
          "value": 800,
          "end_time": "2024-09-11T00:00:00+0000"
        }
      ],
      "title": "Reach",
      "description": "Total number of unique users who have viewed at least one of the IG User's IG Media",
      "id": "12345_reach"
    }
  ]
}
```
### Growth Trends

Calculate and return growth trends for the Instagram account.

#### Endpoint

```
GET /growth-trends
```

#### Query Parameters

| Parameter | Type   | Required | Description                                                        |
|-----------|--------|----------|--------------------------------------------------------------------|
| period    | string | Yes      | Time period for growth calculation. Format: "XYd" where XY is number of days |

#### Example Request

```
GET /growth-trends?period=30d
```

#### Example Response

```json
{
  "trends": [
    {
      "metric": "Follower Growth Rate",
      "current_value": 1100,
      "previous_value": 1000,
      "growth_rate": 10.0
    },
    {
      "metric": "Engagement Rate Change",
      "current_value": 0.05,
      "previous_value": 0.04,
      "growth_rate": 25.0
    }
  ]
}
```

#### Response Description

The response contains an array of trend objects, each representing a growth metric:

- `metric`: The name of the growth metric
- `current_value`: The current value of the metric
- `previous_value`: The previous value of the metric (from the start of the period)
- `growth_rate`: The calculated growth rate as a percentage

#### Notes

- The growth rate is calculated as: ((current_value - previous_value) / previous_value) * 100
- If the previous value is 0, the growth rate is set to 100% if there's any increase, or 0% if there's no change
- The API currently provides growth trends for follower count and engagement rate

#### Error Responses

| Status Code | Description                                             |
|-------------|---------------------------------------------------------|
| 400         | Bad Request - Invalid period format                     |
| 401         | Unauthorized - Invalid or missing access token          |
| 429         | Too Many Requests - Rate limit exceeded                 |
| 500         | Internal Server Error - Something went wrong on our end |

For more details on error responses, see the [Error Handling](#error-handling) section.

### Top Posts

Retrieve top-performing posts based on engagement metrics.

#### Endpoint

```
GET /top-posts
```

#### Query Parameters

| Parameter  | Type    | Required | Description                                                       |
|------------|---------|----------|-------------------------------------------------------------------|
| limit      | integer | No       | Number of top posts to retrieve. Default: 5, Max: 50              |
| time_range | string  | Yes      | Time range for posts. Format: "XYd" where XY is number of days    |

#### Example Request

```
GET /top-posts?limit=3&time_range=7d
```

#### Example Response

```json
{
  "top_posts": [
    {
      "id": "12345",
      "permalink": "https://www.instagram.com/p/ABC123/",
      "caption": "Check out our new product!",
      "like_count": 500,
      "comments_count": 50,
      "engagement_score": 550
    },
    {
      "id": "67890",
      "permalink": "https://www.instagram.com/p/DEF456/",
      "caption": "Behind the scenes at our photoshoot",
      "like_count": 450,
      "comments_count": 75,
      "engagement_score": 525
    },
    {
      "id": "13579",
      "permalink": "https://www.instagram.com/p/GHI789/",
      "caption": "Customer spotlight: @username",
      "like_count": 400,
      "comments_count": 100,
      "engagement_score": 500
    }
  ]
}
```

#### Response Description

The response contains an array of top post objects, each representing a high-performing post:

- `id`: The unique identifier of the post
- `permalink`: The permanent URL of the post on Instagram
- `caption`: The caption of the post (may be truncated if very long)
- `like_count`: The number of likes the post has received
- `comments_count`: The number of comments on the post
- `engagement_score`: A calculated score based on likes and comments

#### Notes

- Posts are ranked based on their engagement score, which is calculated as the sum of likes and comments
- The time range is limited to a maximum of 30 days in the past
- The response is sorted in descending order of engagement score

#### Error Responses

| Status Code | Description                                             |
|-------------|---------------------------------------------------------|
| 400         | Bad Request - Invalid limit or time_range format        |
| 401         | Unauthorized - Invalid or missing access token          |
| 429         | Too Many Requests - Rate limit exceeded                 |
| 500         | Internal Server Error - Something went wrong on our end |





