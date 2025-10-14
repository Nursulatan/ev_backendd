from fastapi import APIRouter

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/panel")
def get_admin_panel():
    return {"message": "Admin panel endpoint working!"}
