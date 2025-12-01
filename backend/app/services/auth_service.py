import json
import os
import base64
import requests
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from app.config import settings
from fastapi import Request

def get_database(request: Request):
    return request.app.mongodb

def get_google_flow(state=None):
    return Flow.from_client_config(
        client_config={
            "web": {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [settings.GOOGLE_REDIRECT_URI]
            }
        },
        scopes=settings.GMAIL_SCOPES,
        redirect_uri=settings.GOOGLE_REDIRECT_URI,
        state=state
    )

def generate_auth_url():
    flow = get_google_flow()
    auth_url, state = flow.authorization_url(access_type="offline", prompt="consent", include_granted_scopes="true")
    return auth_url, state

async def exchange_code_for_tokens(code: str):
    flow = get_google_flow()
    flow.fetch_token(code=code)
    
    user_info_service = build('oauth2', 'v2', credentials=flow.credentials)
    user_info = user_info_service.userinfo().get().execute()
    
    return flow.credentials, user_info['name'], user_info['email']

async def save_credentials_securely(request: Request, creds: Credentials, username: str, email: str) -> str:
    db = get_database(request)
    collection = db[settings.MONGO_COLLECTION_NAME]
    
    session_id = base64.urlsafe_b64encode(os.urandom(32)).decode('utf-8')
    
    user_data = {
        "_id": session_id, 
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "scopes": creds.scopes,
        "username": username,
        "email": email
    }
    
    await collection.insert_one(user_data)
    return session_id

async def load_and_refresh_tokens(request: Request, session_id: str):
    db = get_database(request)
    collection = db[settings.MONGO_COLLECTION_NAME]
    
    user_data = await collection.find_one({"_id": session_id})
    
    if not user_data:
        return None

    creds = Credentials(
        token=user_data["token"],
        refresh_token=user_data.get("refresh_token"),
        token_uri=user_data["token_uri"],
        client_id=user_data["client_id"],
        client_secret=user_data["client_secret"],
        scopes=user_data.get("scopes")
    )
    
    try:
        print(f"[auth_service] loaded creds.scopes: {creds.scopes}")
    except Exception:
        pass

    if not creds.valid:
        if creds.refresh_token:
            creds.refresh(Request())
            try:
                tokeninfo_resp = requests.get(
                    "https://www.googleapis.com/oauth2/v3/tokeninfo",
                    params={"access_token": creds.token},
                    timeout=10
                )
                if tokeninfo_resp.status_code == 200:
                    tokeninfo = tokeninfo_resp.json()
                    granted_scopes = tokeninfo.get("scope", "").split()
                    print(f"[auth_service] tokeninfo scopes after refresh: {granted_scopes}")
                    await collection.update_one(
                        {"_id": session_id},
                        {"$set": {"token": creds.token, "scopes": granted_scopes}}
                    )
                else:
                    await collection.update_one(
                        {"_id": session_id},
                        {"$set": {"token": creds.token}}
                    )
            except Exception as ex:
                print(f"[auth_service] Warning: could not verify token scopes after refresh: {ex}")
                await collection.update_one(
                    {"_id": session_id},
                    {"$set": {"token": creds.token}}
                )
        else:
            await collection.delete_one({"_id": session_id})
            return None

    if creds.valid and creds.token:
        try:
            tokeninfo_resp = requests.get(
                "https://www.googleapis.com/oauth2/v3/tokeninfo",
                params={"access_token": creds.token},
                timeout=10
            )
            if tokeninfo_resp.status_code == 200:
                tokeninfo = tokeninfo_resp.json()
                granted_scopes = tokeninfo.get("scope", "").split()
                print(f"[auth_service] tokeninfo scopes (valid token): {granted_scopes}")
                await collection.update_one(
                    {"_id": session_id},
                    {"$set": {"scopes": granted_scopes}}
                )
        except Exception as ex:
            print(f"[auth_service] Warning: could not verify token scopes for valid token: {ex}")

    return creds, user_data["username"]

async def delete_session(request: Request, session_id: str):
    db = get_database(request)
    collection = db[settings.MONGO_COLLECTION_NAME]
    await collection.delete_one({"_id": session_id})
