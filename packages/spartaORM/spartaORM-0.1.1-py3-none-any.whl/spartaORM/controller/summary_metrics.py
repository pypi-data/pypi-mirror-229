from spartaORM.controller.base import BaseController
from spartaORM.models.summary_metrics import SummaryMetricsModel


class SummaryMetrics(BaseController):
    def __init__(self, database_url: str) -> None:
        super().__init__(database_url=database_url)

    def add(self, **kwargs):
        summary_metrics_entry = SummaryMetricsModel(**kwargs)

        return self.create_entry(summary_metrics_entry)
