# Ins_api

# Facebook and Instagram Account Setup SOP

This document outlines the steps to set up Facebook and Instagram accounts, link them together, and obtain the Instagram account ID for API use.

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
---
Noted that the ACCESS_LONG_LIVED_TOKEN (long-lived access tokens) for the Instagram Graph API typically last for about 60 days. So need to update in every 60 days



