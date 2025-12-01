from fastapi import APIRouter, Request, HTTPException, status
from fastapi.responses import RedirectResponse
from app.services import auth_service

router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"]
)

FRONTEND_DASHBOARD_URL = "https://your-app-name.vercel.app/dashboard" 

@router.get("/login")
async def google_login(request: Request):
    """Initiates the Google OAuth process."""
    try:
        auth_url, _ = auth_service.generate_auth_url()
        return RedirectResponse(auth_url)
    except Exception as e:
        print(f"Auth initiation error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not initiate Google login.")

@router.get("/callback")
async def google_auth_callback(request: Request, code: str = None, error: str = None):
    """Callback endpoint to handle the OAuth response from Google."""
    if error or not code:
        error_detail = error or "User denied access or login failed."
        return RedirectResponse(f"{FRONTEND_DASHBOARD_URL}?auth_error={error_detail}")

    try:
        creds, username, email = await auth_service.exchange_code_for_tokens(code)
        
        session_id = await auth_service.save_credentials_securely(request, creds, username, email)
        request.session["user_session_id"] = session_id
        
        return RedirectResponse(FRONTEND_DASHBOARD_URL, status_code=status.HTTP_302_FOUND)
        
    except Exception as e:
        print(f"Token exchange error: {e}")
        return RedirectResponse(f"{FRONTEND_DASHBOARD_URL}?auth_error=Authentication failed. Please try again or check permissions.")


@router.get("/logout")
async def logout(request: Request):
    """Clears the session from the browser and the database."""
    session_id = request.session.pop("user_session_id", None)
    
    if session_id:
        await auth_service.delete_session(request, session_id)
        
    return RedirectResponse("https://your-app-name.vercel.app/")