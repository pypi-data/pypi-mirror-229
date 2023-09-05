from spartaORM.controller.base import BaseController
from spartaORM.models.race import RaceModel


class Race(BaseController):
    def __init__(self, database_url: str) -> None:
        super().__init__(database_url=database_url)

    def add(self, **kwargs):
        race_entry = RaceModel(**kwargs)

        return self.create_entry(race_entry)
