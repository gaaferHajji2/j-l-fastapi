from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.post import Post
from app.models.category import Category
from app.core.errors import NotFoundError, ConflictError

class ProductCRUD:
    def __init__(self, db: AsyncSession):
        pass

    async def get_post_with_relations(self, post_id: int) -> Optional[Post]:
        result = await self.db.execute(
            select(Post).options(
                selectinload(Post.author),
                selectinload(Post.comments),
                selectinload(Post.categories)
            ).where(Post.id == post_id)
        )
        return result.scalar_one_or_none()

    async def add_category_to_post(self, post_id: int, category_id: int) -> Post:
        post = await self.get_post_with_relations(post_id)
        if not post:
            raise NotFoundError("Post", post_id)
        
        result = await self.db.execute(
            select(Category).where(Category.id == category_id)
        )
        category = result.scalar_one_or_none()
        
        if not category:
            raise NotFoundError("Category", category_id)
        
        # Check if category already added
        if category in post.categories:
            raise ConflictError(f"Category {category_id} is already added to post {post_id}")
        
        post.categories.append(category)
        await self.db.commit()
        await self.db.refresh(post)
        return post
