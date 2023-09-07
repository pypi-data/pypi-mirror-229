from typing import List

import ai.h2o.featurestore.api.v1.CoreService_pb2 as pb

from ..entities.backfill_job import BackfillJob
from ..entities.base_job import BaseJob
from ..entities.compute_recommendation_classifiers_job import ComputeRecommendationClassifiersJob
from ..entities.compute_statistics_job import ComputeStatisticsJob
from ..entities.create_ml_dataset_job import CreateMLDatasetJob
from ..entities.extract_schema_job import ExtractSchemaJob
from ..entities.ingest_job import IngestJob
from ..entities.materialization_online_job import MaterializationOnlineJob
from ..entities.retrieve_job import RetrieveJob
from ..entities.revert_ingest_job import RevertIngestJob


class Jobs:
    def __init__(self, stub):
        self._stub = stub

    @staticmethod
    def _create_job(stub, job_proto):
        job_id = pb.JobId(job_id=job_proto.job_id)
        if job_proto.job_type == pb.JobType.Ingest:
            return IngestJob(stub, job_id)
        elif job_proto.job_type == pb.JobType.ExtractSchema:
            return ExtractSchemaJob(stub, job_id)
        elif job_proto.job_type == pb.JobType.Retrieve:
            return RetrieveJob(stub, job_id)
        elif job_proto.job_type == pb.JobType.MaterializationOnline:
            return MaterializationOnlineJob(stub, job_id)
        elif job_proto.job_type == pb.JobType.ComputeStatistics:
            return ComputeStatisticsJob(stub, job_id)
        elif job_proto.job_type == pb.JobType.Revert:
            return RevertIngestJob(stub, job_id)
        elif job_proto.job_type == pb.JobType.ComputeRecommendationClassifiers:
            return ComputeRecommendationClassifiersJob(stub, job_id)
        elif job_proto.job_type == pb.JobType.CreateMLDataset:
            return CreateMLDatasetJob(stub, job_id)
        elif job_proto.job_type == pb.JobType.Backfill:
            return BackfillJob(stub, job_id)

    def list(self, active=True, job_type=pb.JobType.Unknown) -> List[BaseJob]:
        request = pb.ListJobsRequest(active=active, job_type=job_type)
        resp = self._stub.ListJobs(request)
        return [Jobs._create_job(self._stub, job_proto) for job_proto in resp.jobs]

    def get(self, job_id: str) -> BaseJob:
        request = pb.JobId(job_id=job_id)
        job_proto = self._stub.GetJob(request)
        return Jobs._create_job(self._stub, job_proto)

    def __repr__(self):
        return "This class wraps together methods working with jobs"
