from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from src.api.response_models.schemas.post import PostResponse, PostCreate, PostWithUserResponse, PostListResponse, \
    MyPostListResponse, PostUpdate
from src.services import post_service
from src.services.auth import AuthService
from src.services.post_service import PostService


post_router = APIRouter(prefix="/posts", tags=["Posts"])

@post_router.post("/", response_model=PostResponse ,status_code=status.HTTP_201_CREATED)
async def create_post(
    post_data: PostCreate,
    current_user: Any = Depends(AuthService.get_current_user),
    service: PostService = Depends()
):
    new_post= service.create_post(user_id=current_user["id"],post_data=post_data)
    if not new_post :
        raise HTTPException(status_code=500, detail="متاسفانه پست ساخته نشد")
    return new_post

@post_router.get(
    "/",
    response_model=PostListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get all published posts (Explore)",
    description="Get all published posts with pagination metadata and author info")
async def get_all_posts(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=50, description="Items per page"),
    post_service: PostService = Depends(),
    search: Optional[str] = Query(None, min_length=2),
    post_type: Optional[str] = Query(None, min_length=2),
    tag: Optional[str] = Query(None, min_length=2),
):
    return await post_service.get_published_posts(page=page, size=size , post_type=post_type, search=search , tag=tag)

@post_router.get("/s/{slug}" , response_model=PostWithUserResponse , status_code=status.HTTP_200_OK ,summary="Get a post by slug")
async def get_post(
    slug: str,
    post_service: PostService = Depends(),
):
    post = await post_service.get_post_by_slug(slug)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="امکان نمایش وجود ندارد؛ پستی با این مشخصات یافت نشد!"
        )
    return post

@post_router.get(
    "/user/{user_id}",
    response_model=PostListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get all published posts of a specific user",
    description="Get a user's post grid with pagination metadata"
)
async def get_user_posts(
    user_id: int,
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=50, description="Items per page"),
    post_type: Optional[str] = Query(None, min_length=2),
    post_service: PostService = Depends(),
):
    return await post_service.get_published_posts(
        page=page,
        size=size,
        post_type=post_type,
        user_id=user_id
    )

@post_router.get(
    "/me",
    response_model=MyPostListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get all my posts (Dashboard)",
    description="Get all posts of the currently authenticated user, including drafts"
)
async def get_my_posts(
        page: int = Query(1, ge=1, description="Page number"),
        size: int = Query(10, ge=1, le=50, description="Items per page"),
        post_type: Optional[str] = Query(None, min_length=2),
        post_service: PostService = Depends(),
        current_user: Any = Depends(AuthService.get_current_user),
):
    return await post_service.get_my_posts(
        page=page,
        size=size,
        post_type=post_type,
        user_id=current_user["id"],
    )


@post_router.patch("/{post_id}" , response_model=PostResponse , status_code=status.HTTP_200_OK)
async def update_post(
        post_id: int,
        update_data: PostUpdate,
        current_user: Any = Depends(AuthService.get_current_user),
        post_service: PostService = Depends()
):
    update_dict= update_data.model_dump(exclude_unset=True)

    updated_post=await post_service.update_post(
        post_id=post_id,
        user_id=current_user["id"],
        post_data=update_dict
    )

    if not updated_post :
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="پستی یافت نشد یا شما اجازه ویرایش این پست را ندارید!"
        )
    return updated_post


@post_router.delete("/{post_id}" , status_code=status.HTTP_200_OK)
async def delete_post(
        post_id: int,
        current_user: Any = Depends(AuthService.get_current_user),
        post_service: PostService = Depends()
):
    return await post_service.delete_post(post_id=post_id , user_id=current_user["id"])
