from fastapi import Request, Depends, HTTPException, status
from app.services.auth_service import load_and_refresh_tokens

def get_session_id(request: Request) -> str:
    """Extracts the session ID from the request session."""
    session_id = request.session.get("user_session_id")
    if not session_id:
        return None
    return session_id

async def get_current_user_credentials(request: Request, session_id: str = Depends(get_session_id)):
    """
    Loads and refreshes Google credentials from the database.
    Returns the (creds, username) tuple.
    """
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired or not authenticated. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    creds_data = await load_and_refresh_tokens(request, session_id)
    
    if not creds_data:
        request.session.pop("user_session_id", None)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalid, revoked, or session expired. Please re-authenticate.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return creds_data