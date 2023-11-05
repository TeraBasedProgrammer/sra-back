from app.repository.tag import TagRepository


class TagService:
    def __init__(self, tag_repository) -> None:
        self.tag_repository: TagRepository = tag_repository
