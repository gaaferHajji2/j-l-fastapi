from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.post import Post

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
