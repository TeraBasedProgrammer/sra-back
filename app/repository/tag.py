from app.models.db.users import Tag
from app.repository.base import BaseRepository


class TagRepository(BaseRepository):
    model = Tag
