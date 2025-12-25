from fastapi import Header, HTTPException, Request, Depends


def auth_guard(
    request: Request,
    x_api_key: str = Header(..., alias="X-API-KEY"),
    x_user_id: str = Header(..., alias="X-USER-ID"),
) -> str:
    if x_api_key != request.app.state.settings.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

    user_id = (x_user_id or "").strip()
    if not user_id:
        raise HTTPException(status_code=400, detail="X-USER-ID is required")

    return user_id


UserIdDep = Depends(auth_guard)