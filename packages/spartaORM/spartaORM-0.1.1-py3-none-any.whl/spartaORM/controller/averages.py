from spartaORM.controller.base import BaseController
from spartaORM.models.averages import AveragesModel


class Averages(BaseController):
    def __init__(self, database_url: str) -> None:
        super().__init__(database_url=database_url)

    def add(self, **kwargs):
        averages_entry = AveragesModel(**kwargs)

        return self.create_entry(averages_entry)
