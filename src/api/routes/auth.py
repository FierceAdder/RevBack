"""Authentication and Tenant Management API endpoints."""

from datetime import datetime, timezone
import re
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.db.session import get_db
from src.models.db_models import User, Tenant, ApiKey, UserRole
from src.auth.jwt import hash_password, verify_password, create_access_token, generate_api_key
from src.auth.middleware import get_current_user, get_current_admin

router = APIRouter(prefix="/auth", tags=["Authentication & Multi-Tenancy"])


# ---------------- Request / Response Schemas ---------------- #

class RegisterRequest(BaseModel):
    company_name: str = Field(..., min_length=2, max_length=255)
    full_name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=6)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TenantResponse(BaseModel):
    id: str
    name: str
    slug: str
    razorpay_key_id: Optional[str] = None


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    tenant_id: Optional[str] = None
    tenant: Optional[TenantResponse] = None


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class CreateApiKeyRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=128)
    scope: str = Field(default="ADMIN", description="READ, WRITE, ADMIN")


class ApiKeyResponse(BaseModel):
    id: str
    name: str
    prefix: str
    scope: str
    created_at: str
    raw_key: Optional[str] = None


class InviteTeamMemberRequest(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=255)
    role: str = Field(default="SUPERVISOR", description="ADMIN, SUPERVISOR, VIEWER")


# ---------------- Route Handlers ---------------- #

@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register_tenant_and_admin(
    payload: RegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    """Registers a new merchant organization (Tenant) and root administrator account."""
    # Check if email is already registered
    existing_user = await db.execute(select(User).where(User.email == payload.email))
    if existing_user.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists",
        )

    # Generate slug from company name
    slug = re.sub(r"[^a-z0-9]+", "-", payload.company_name.lower()).strip("-")
    base_slug = slug
    counter = 1
    while True:
        existing_tenant = await db.execute(select(Tenant).where(Tenant.slug == slug))
        if not existing_tenant.scalars().first():
            break
        slug = f"{base_slug}-{counter}"
        counter += 1

    # Create Tenant
    tenant = Tenant(
        name=payload.company_name,
        slug=slug,
    )
    db.add(tenant)
    await db.flush()

    # Create Administrator User
    user = User(
        tenant_id=tenant.id,
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=hash_password(payload.password),
        role=UserRole.ADMIN,
        is_active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    await db.refresh(tenant)

    # Generate Access Token
    token = create_access_token({
        "sub": user.id,
        "email": user.email,
        "tenant_id": tenant.id,
        "role": user.role.value,
    })

    return AuthResponse(
        access_token=token,
        user=UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            role=user.role.value,
            tenant_id=tenant.id,
            tenant=TenantResponse(
                id=tenant.id,
                name=tenant.name,
                slug=tenant.slug,
                razorpay_key_id=tenant.razorpay_key_id,
            ),
        ),
    )


@router.post("/login", response_model=AuthResponse)
async def login(
    payload: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """Authenticates credentials and returns JWT bearer token."""
    query = select(User).where(User.email == payload.email).options(selectinload(User.tenant))
    res = await db.execute(query)
    user = res.scalars().first()

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled",
        )

    tenant_dict = None
    if user.tenant:
        tenant_dict = TenantResponse(
            id=user.tenant.id,
            name=user.tenant.name,
            slug=user.tenant.slug,
            razorpay_key_id=user.tenant.razorpay_key_id,
        )

    token = create_access_token({
        "sub": user.id,
        "email": user.email,
        "tenant_id": user.tenant_id,
        "role": user.role.value,
    })

    return AuthResponse(
        access_token=token,
        user=UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            role=user.role.value,
            tenant_id=user.tenant_id,
            tenant=tenant_dict,
        ),
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Returns profile and tenant information for current authenticated user."""
    tenant_dict = None
    if current_user.tenant:
        tenant_dict = TenantResponse(
            id=current_user.tenant.id,
            name=current_user.tenant.name,
            slug=current_user.tenant.slug,
            razorpay_key_id=current_user.tenant.razorpay_key_id,
        )

    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role.value,
        tenant_id=current_user.tenant_id,
        tenant=tenant_dict,
    )


@router.post("/api-keys", response_model=ApiKeyResponse, status_code=status.HTTP_201_CREATED)
async def create_new_api_key(
    payload: CreateApiKeyRequest,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Generates a new API key for the authenticated tenant. (Key is shown only once)."""
    if not current_user.tenant_id:
        raise HTTPException(status_code=400, detail="User is not associated with a merchant tenant")

    raw_key, key_hash, key_prefix = generate_api_key()

    api_key = ApiKey(
        tenant_id=current_user.tenant_id,
        name=payload.name,
        key_hash=key_hash,
        key_prefix=key_prefix,
        scope=payload.scope,
        is_active=True,
    )
    db.add(api_key)
    await db.commit()
    await db.refresh(api_key)

    return ApiKeyResponse(
        id=api_key.id,
        name=api_key.name,
        prefix=api_key.key_prefix,
        scope=api_key.scope,
        created_at=api_key.created_at.isoformat(),
        raw_key=raw_key,
    )


@router.get("/api-keys", response_model=List[ApiKeyResponse])
async def list_api_keys(
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Lists all active API keys for the current merchant tenant."""
    if not current_user.tenant_id:
        return []

    query = (
        select(ApiKey)
        .where(ApiKey.tenant_id == current_user.tenant_id, ApiKey.is_active == True)
        .order_by(ApiKey.created_at.desc())
    )
    res = await db.execute(query)
    keys = res.scalars().all()

    return [
        ApiKeyResponse(
            id=k.id,
            name=k.name,
            prefix=k.key_prefix,
            scope=k.scope,
            created_at=k.created_at.isoformat(),
            raw_key=None,
        )
        for k in keys
    ]


@router.delete("/api-keys/{key_id}", status_code=status.HTTP_200_OK)
async def revoke_api_key(
    key_id: str,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Revokes an API key belonging to the tenant."""
    query = select(ApiKey).where(ApiKey.id == key_id, ApiKey.tenant_id == current_user.tenant_id)
    res = await db.execute(query)
    key = res.scalars().first()
    if not key:
        raise HTTPException(status_code=404, detail="API key not found")

    key.is_active = False
    await db.commit()
    return {"status": "revoked", "key_id": key_id}


@router.get("/team", response_model=List[UserResponse])
async def list_team_members(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Lists all team members associated with the tenant."""
    if not current_user.tenant_id:
        return [
            UserResponse(
                id=current_user.id,
                email=current_user.email,
                full_name=current_user.full_name,
                role=current_user.role.value,
                tenant_id=None,
                tenant=None,
            )
        ]

    query = select(User).where(User.tenant_id == current_user.tenant_id).order_by(User.created_at.asc())
    res = await db.execute(query)
    users = res.scalars().all()

    return [
        UserResponse(
            id=u.id,
            email=u.email,
            full_name=u.full_name,
            role=u.role.value,
            tenant_id=u.tenant_id,
            tenant=None,
        )
        for u in users
    ]


@router.post("/team", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def invite_team_member(
    payload: InviteTeamMemberRequest,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Invites a new team member with a specified role."""
    if not current_user.tenant_id:
        raise HTTPException(status_code=400, detail="Cannot invite members without a tenant")

    # Check if user already exists
    existing = await db.execute(select(User).where(User.email == payload.email))
    if existing.scalars().first():
        raise HTTPException(status_code=400, detail="A user with this email already exists")

    try:
        assigned_role = UserRole[payload.role.upper()]
    except KeyError:
        assigned_role = UserRole.SUPERVISOR

    new_user = User(
        tenant_id=current_user.tenant_id,
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=hash_password("TemporaryPass123!"),
        role=assigned_role,
        is_active=True,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return UserResponse(
        id=new_user.id,
        email=new_user.email,
        full_name=new_user.full_name,
        role=new_user.role.value,
        tenant_id=new_user.tenant_id,
        tenant=None,
    )

