from spartaORM.controller.base import BaseController
from spartaORM.models.pacing import PacingModel


class Pacing(BaseController):
    def __init__(self, database_url: str) -> None:
        super().__init__(database_url=database_url)

    def add(self, **kwargs):
        pacing_entry = PacingModel(**kwargs)

        return self.create_entry(pacing_entry)
