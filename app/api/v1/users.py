from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.api.dependencies import get_current_user
from app.core.security import hash_password, verify_password
from app.database import get_session
from app.models.user import User
from app.schemas.user import ChangePassword, UserResponse, UserUpdate

router = APIRouter()


@router.get("/me", response_model=UserResponse)
def get_my_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=UserResponse)
def update_my_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    update_data = user_update.model_dump(exclude_unset=True)

    if "email" in update_data:
        existing_user = session.exec(
            select(User).where(
                User.email == update_data["email"], User.id != current_user.id
            )
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Email already in use"
            )

    for key, value in update_data.items():
        setattr(current_user, key, value)

    session.add(current_user)
    session.commit()
    session.refresh(current_user)

    return current_user


@router.put("/me/password")
def change_password(
    password_data: ChangePassword,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    if not verify_password(
        password_data.current_password, current_user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )

    current_user.hashed_password = hash_password(password_data.new_password)

    session.add(current_user)
    session.commit()

    return {"message": "Password updated successfully"}
