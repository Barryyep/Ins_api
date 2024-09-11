import requests


def get_instagram_account_id(access_token):
    # # Step 1: Get the Facebook Page ID
    # url = "https://graph.facebook.com/v20.0/me/accounts"
    # params = {"access_token": access_token}
    # response = requests.get(url, params=params)

    # if response.status_code != 200:
    #     print(f"Error response: {response.text}")
    #     raise Excepti1on(f"Failed to get Facebook Pages: {response.text}")

    # data = response.json()
    # print(f"API Response: {data}")  # Debug print

    # pages = data.get("data", [])
    # if not pages:
    #     print("No pages found in the response")
    #     raise Exception(
    #         "No Facebook Pages found. Check your access token and permissions."
    #     )

    # page_id = pages[0]["id"]
    # print(f"Using Page ID: {page_id}")  # Debug print

    # Step 2: Get the Instagram Business Account ID
    url = f"https://graph.facebook.com/v20.0/385167584687311"
    params = {"fields": "instagram_business_account", "access_token": access_token}
    response = requests.get(url, params=params)

    if response.status_code != 200:
        print(f"Error response: {response.text}")
        raise Exception(f"Failed to get Instagram Business Account: {response.text}")

    data = response.json()
    print(f"Instagram Business Account Response: {data}")  # Debug print

    instagram_account = data.get("instagram_business_account")
    if not instagram_account:
        raise Exception("No Instagram Business Account found for this Page")

    return instagram_account["id"]


# Usage
ACCESS_TOKEN = "EAB1eTbmRsuYBO0RE1DAdZBZCZC5LNnbZBNgLpFZAqebbexkhzoAQG8ndk2WdaO6PXorJqZBdFAPrFJ8ZAxigmwKlrnfLnaA2LYOcip1WCWE57BzCio3ZAes0hAITGHZCzNPeYFkomlh4U7LKbeYhLoiday8kEHlm8fXUd1nJz5mBUbyMCZCYpO1sA53vHZAMqPxOUAYOWO3xDTfsaBv7cDGwdZCtnM22ZBgZDZD"
try:
    instagram_account_id = get_instagram_account_id(ACCESS_TOKEN)
    print(f"Instagram Account ID: {instagram_account_id}")
except Exception as e:
    print(f"Error: {str(e)}")


# Additional debug: Check token info
def debug_token(access_token):
    app_id = "8266462243435238"
    app_secret = "5d313efb010943a344fa6324a08518e9"

    url = f"https://graph.facebook.com/debug_token"
    params = {"input_token": access_token, "access_token": f"{app_id}|{app_secret}"}
    response = requests.get(url, params=params)
    print(f"Token Debug Info: {response.json()}")


debug_token(ACCESS_TOKEN)
