from spartaORM.controller.base import BaseController
from spartaORM.models.official_results import OfficialResultsModel


class OfficialResults(BaseController):
    def __init__(self, database_url: str) -> None:
        super().__init__(database_url=database_url)

    def add(self, **kwargs):
        official_results_entry = OfficialResultsModel(**kwargs)

        return self.create_entry(official_results_entry)
