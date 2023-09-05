from spartaORM.controller.base import BaseController
from spartaORM.models.segment_metrics import SegmentMetricsModel


class SegmentMetrics(BaseController):
    def __init__(self, database_url: str) -> None:
        super().__init__(database_url=database_url)

    def add(self, **kwargs):
        segment_metrics_entry = SegmentMetricsModel(**kwargs)

        return self.create_entry(segment_metrics_entry)
