import math
import re
from typing import Optional

from fastapi import HTTPException
from psycopg2.extras import DictCursor

from src.repositories.post_repository import PostRepository
from src.repositories.user_repository import UserRepository
from src.api.response_models.schemas.post import PostCreate, PostType, PostUpdate
import uuid


class PostService:
    def __init__(self):
        self.post_repository = PostRepository()
        self.user_repository = UserRepository()

    def generate_slug(self, title: str) -> str:

        slug = re.sub(r'[^\w\s-]', '', title, flags=re.UNICODE).strip().lower()
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug

    def create_post(self, user_id: int, post_data: PostCreate):

        post_dict = post_data.model_dump()
        post_dict['user_id'] = user_id

        tags = [tag.lower() for tag in post_dict.pop("tags", [])]

        post_dict.setdefault("extra_data", {})
        post_dict["extra_data"]["tags"] = tags

        if post_dict.get('title'):
            base_slug = self.generate_slug(post_dict['title'])
            final_slug = base_slug

            while self.post_repository.is_slug_exists(final_slug):
                random_suffix = str(uuid.uuid4())
                final_slug = f"{base_slug}-{random_suffix}"

            post_dict['slug'] = final_slug
        else:
            post_dict['slug'] = None

        new_post = self.post_repository.create(post_dict)

        if new_post and new_post.get('is_published') is True:
            reputation_scores ={
                PostType.THOUGHT :2,
                PostType.MEDIA :3
            }

            specialty_scores ={
                PostType.PORTFOLIO :2,
                PostType.ARTICLE :5
            }

            current_post_type = post_dict.get('post_type')

            if current_post_type in reputation_scores:
                reward = reputation_scores[current_post_type]
                self.user_repository.increase_reputation(user_id, reward)
                print(f"⭐ {reward} امتیاز اعتبار عمومی به کاربر {user_id} اضافه شد.")

            elif current_post_type in specialty_scores:
                reward = specialty_scores[current_post_type]
                self.user_repository.increase_specialty_score(user_id, reward)
                print(f"🔥 {reward} امتیاز تخصص به کاربر {user_id} اضافه شد.")

        return new_post

    async def get_published_posts(self , page: int =1 , size: int =10 ,post_type: str = None, search: str = None , tag:str = None , user_id:int = None  ):
        offset = (page - 1) * size
        total_count = self.post_repository.get_posts_counts(post_type=post_type, search=search , tag=tag , user_id=user_id)
        posts = self.post_repository.get_all_published_posts(
            limit=size, offset=offset ,post_type=post_type,
            search=search , tag=tag ,user_id=user_id)
        total_pages = math.ceil(total_count / size) if size >0 else 0
        return {
            "items": posts,
            "total_count": total_count,
            "page": page,
            "size": size,
            "total_pages": total_pages,
        }

    async def get_post_by_slug(self, slug: str):
        post = self.post_repository.get_post_by_slug(slug)
        if post is None:
            return None
        return post

    async def get_my_posts(self , user_id: int ,page:int =1 ,size:int=10 ,post_type:Optional[str]=None):
        offset = (page - 1) * size
        total_count =self.post_repository.get_my_posts_count(user_id=user_id, post_type=post_type)
        posts = self.post_repository.get_my_posts(user_id=user_id,limit=size,offset =offset ,post_type=post_type)
        total_pages = math.ceil(total_count / size) if size >0 else 0
        return {
            "items": posts,
            "total_count": total_count,
            "page": page,
            "size": size,
            "total_pages": total_pages,
        }

    async def update_post(self, post_id:int , user_id:int , post_data:dict):
        current_post = self.post_repository.get_post_by_id_and_user(post_id=post_id, user_id=user_id)
        if current_post is None:
            return None

        cleaned_data = {k:v for k , v in post_data.items() if v is not None}

        if "tags" in cleaned_data:
            new_tags = [tag.lower() for tag in cleaned_data.pop("tags", [])]
            extra_data = cleaned_data.get("extra_data") or current_post.get("extra_data") or {}
            extra_data["tags"] = new_tags
            cleaned_data["extra_data"] = extra_data


        if "title" in cleaned_data and cleaned_data["title"] != current_post["title"]:
            base_slug = self.generate_slug(cleaned_data['title'])
            final_slug = base_slug

            while self.post_repository.is_slug_exists(final_slug):
                random_suffix = str(uuid.uuid4())
                final_slug = f"{base_slug}-{random_suffix}"

            cleaned_data['slug'] = final_slug
            pass

        if cleaned_data.get("is_published") is True and current_post["is_published"] is False:
            reputation_scores = {
                PostType.THOUGHT: 2,
                PostType.MEDIA: 3
            }

            specialty_scores = {
                PostType.PORTFOLIO: 2,
                PostType.ARTICLE: 5
            }

            current_post_type = cleaned_data.get('post_type') or current_post.get('post_type')

            if current_post_type in reputation_scores:
                reward = reputation_scores[current_post_type]
                self.user_repository.increase_reputation(user_id, reward)
                print(f"⭐ {reward} امتیاز اعتبار عمومی به کاربر {user_id} اضافه شد.")

            elif current_post_type in specialty_scores:
                reward = specialty_scores[current_post_type]
                self.user_repository.increase_specialty_score(user_id, reward)
                print(f"🔥 {reward} امتیاز تخصص به کاربر {user_id} اضافه شد.")

            pass

        return self.post_repository.update(post_id, cleaned_data)

    async def delete_post(self, post_id:int , user_id:int) ->bool:
        current_post=self.post_repository.get_post_by_id_and_user(post_id=post_id, user_id=user_id)
        if current_post is None:
            return False

        success=self.post_repository.delete(post_id=post_id, user_id=user_id)

        if success and current_post.get("is_published") is True:
            reputation_scores = {
                PostType.THOUGHT: 2,
                PostType.MEDIA: 3
            }

            specialty_scores = {
                PostType.PORTFOLIO: 2,
                PostType.ARTICLE: 5
            }

            current_post_type = current_post.get('post_type') or current_post.get('post_type')
            if current_post_type in reputation_scores:
                penalty = reputation_scores[current_post_type]
                self.user_repository.decrease_reputation(user_id, penalty)
                print(f"📉 {penalty} امتیاز اعتبار عمومی از کاربر {user_id} به دلیل حذف پست کم شد.")

            elif current_post_type in specialty_scores:
                penalty = specialty_scores[current_post_type]
                self.user_repository.decrease_specialty_score(user_id, penalty)
                print(f"📉 {penalty} امتیاز تخصص از کاربر {user_id} به دلیل حذف پست کم شد.")

            return success

