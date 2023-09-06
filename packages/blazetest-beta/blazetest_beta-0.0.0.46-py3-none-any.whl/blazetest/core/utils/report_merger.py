import logging
from typing import List

import boto3
import junitparser

from blazetest.core.utils.exceptions import ReportNotAvailable, ReportNotUploaded

logger = logging.getLogger(__name__)


class ReportMerger:
    """
    Merges reports from S3 Bucket into one file and saves back to the bucket.
    """

    FILE_ENCODING = "utf-8"

    def __init__(
        self,
        stack_name: str,
        region: str,
        s3_bucket_name: str = None,
        aws_access_key_id: str = None,
        aws_secret_access_key: str = None,
    ):
        self.s3_client = boto3.client(
            "s3",
            region_name=region,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )
        self.s3_bucket_name = s3_bucket_name
        self.stack_name = stack_name

    def set_s3_bucket_name(self, s3_bucket_name: str) -> None:
        self.s3_bucket_name = s3_bucket_name

    def merge_reports(self, report_paths: List[str]) -> str:
        merged_report = junitparser.JUnitXml()

        for report_path in report_paths:
            report_data = self.__download_report(report_path)
            junit_report = junitparser.JUnitXml.fromstring(report_data)
            merged_report += junit_report

        merged_report_filename = f"test-session-{self.stack_name}.xml"
        merged_report_filepath = f"merged/{merged_report_filename}"

        self.__upload_report(
            body=merged_report.tostring(),
            path=merged_report_filepath,
        )

        return merged_report_filepath

    def __download_report(self, report_path: str) -> str:
        try:
            response = self.s3_client.get_object(
                Bucket=self.s3_bucket_name, Key=report_path
            )
            report_data = response["Body"].read().decode(self.FILE_ENCODING)
            return report_data
        except Exception as e:
            raise ReportNotAvailable(
                f"Error downloading report {report_path}: {str(e)}"
            )

    def __upload_report(self, body: str, path: str) -> None:
        try:
            self.s3_client.put_object(Body=body, Bucket=self.s3_bucket_name, Key=path)
        except Exception as e:
            raise ReportNotUploaded(f"Error uploading report {path} to S3: {str(e)}")
