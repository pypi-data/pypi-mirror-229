from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import logging
import time
from typing import List, Optional

from blazetest.core.config import MAX_LAMBDA_WORKERS
from blazetest.core.project_config.project_config import BlazetestConfig
from blazetest.core.lambda_.invocation import Invocation
from blazetest.core.run_test.pytest_collect import collect_tests
from blazetest.core.run_test.result_model import TestSessionResult
from blazetest.core.utils.exceptions import ReportNotAvailable, ReportNotUploaded
from blazetest.core.utils.report_merger import ReportMerger
from blazetest.core.utils.utils import remove_junit_report_path

logger = logging.getLogger(__name__)


class TestRunner:
    """
    Class for running tests using Lambda functions.
    This class is responsible for collecting the test items,
    creating the report paths, and invoking the Lambda functions.

    Attributes:
        config (BlazetestConfig): Configuration for running the tests on AWS Lambda.
        lambda_function (Lambda):  Object responsible for interacting with AWS Lambda.

    Methods:
        run_tests(): Collects the test items, creates the report paths,
            and invokes the Lambda functions.
    """

    # Lambda function name, which will be invoked to run tests
    function_name: str = None

    # S3 bucket name, where the reports should be saved
    s3_bucket: str = None

    def __init__(
        self,
        config: BlazetestConfig,
        uuid: str,
        aws_access_key_id: str = None,
        aws_secret_access_key: str = None,
    ):
        """
        Initializes the class with the given config and creates a new Lambda Invocation object.

        :param config: Configuration for running the tests on AWS Lambda.
        :param uuid: Blazetest session UUID.
        """
        self.config = config

        logger.info(
            f"Pytest collection args initialised: {config.pytest.collection_args}"
        )
        logger.info(f"Pytest execution args initiated: {config.pytest.execution_args}")

        stack_name = self.config.aws.get_stack_name(uuid=uuid[:8])
        self.lambda_function = Invocation(
            region=self.config.aws.region,
            stack_name=stack_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )
        self.report_merger = ReportMerger(
            region=self.config.aws.region,
            stack_name=stack_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )
        self.timestamp = self.__get_timestamp_now()

    def get_collected_tests(self):
        return collect_tests(pytest_args=self.config.pytest.collection_args)

    def run_tests(
        self,
        node_ids: List[str],
        flaky_test_retry_enabled: bool = True,
    ) -> Optional[TestSessionResult]:
        """
        Creates the report paths, and invokes the Lambda functions in parallel.
        """
        function_details = self.lambda_function.get_created_lambda_function_details()
        self.function_name = function_details["function_name"]
        self.s3_bucket = function_details["s3_bucket"]
        logger.info(
            f"Lambda function: {self.function_name}, " f"S3 bucket: {self.s3_bucket}",
        )

        logger.info("Invoking tests and running in parallel.. It might take some time")
        tests_results = self.__run_in_parallel(node_ids=node_ids)

        self.__merge_reports(report_paths=tests_results["report_paths"])

        failed_tests = tests_results["failed"]
        failed_tests_after_retry = 0

        if flaky_test_retry_enabled and failed_tests:
            logger.info(
                f"Retrying running {len(failed_tests)} failed tests {self.config.failed_test_retry} times"
            )
            retry_test_results = self.__run_in_parallel(
                node_ids=failed_tests * self.config.failed_test_retry
            )
            failed_tests_after_retry = len(retry_test_results["failed"])

        return TestSessionResult(
            lambda_function_name=self.function_name,
            tests_count=len(node_ids),
            tests_passed=tests_results["passed"],
            duration=tests_results["duration"],
            s3_bucket=self.s3_bucket,
            timestamp=self.timestamp,
            failed_tests_count=len(failed_tests),
            failed_tests_after_retry=failed_tests_after_retry,
        )

    def invoke_lambda(self, node_id: str):
        logger.debug(f"Invoking Lambda with node_id: {node_id}")

        report_path = self.__get_pytest_xml_report_path(node_id=node_id)
        pytest_args = remove_junit_report_path(self.config.pytest.execution_args)

        invocation_result = self.lambda_function.invoke(
            function_name=self.function_name,
            node_id=node_id,
            pytest_args=pytest_args,
            report_path=report_path,
            timestamp=self.timestamp,
        )
        return node_id, invocation_result

    def __run_in_parallel(self, node_ids: List[str]):
        start_time = time.time()

        # TODO: is 1000 appropriate value for workers for threads?
        with ThreadPoolExecutor(max_workers=MAX_LAMBDA_WORKERS) as executor:
            results = list(executor.map(self.invoke_lambda, node_ids))

        tests_passed = sum(
            bool(invocation_result["test_result"]) for _, invocation_result in results
        )
        failed_tests = [
            node_id
            for node_id, invocation_result in results
            if invocation_result is False
        ]
        report_paths = [
            report_path
            for _, invocation_result in results
            for report_path in invocation_result["report_path"]
        ]

        return {
            "passed": tests_passed,
            "failed": list(set(failed_tests)),
            "duration": time.time() - start_time,
            "report_paths": report_paths,
        }

    def __merge_reports(self, report_paths: List[str]) -> Optional[str]:
        """
        Merges the reports saved to s3 bucket using junitparser and saves the final result in the s3 bucket.

        :param report_paths: list of paths to the s3 bucket.

        Returns the path to the merged report.
        """
        self.report_merger.set_s3_bucket_name(s3_bucket_name=self.s3_bucket)

        logger.info("Merging reports")
        try:
            merged_report_path = self.report_merger.merge_reports(
                report_paths=report_paths
            )
        except (ReportNotAvailable, ReportNotUploaded) as e:
            logger.error(f"Error merging reports: {str(e)}")
            return

        logger.info(
            f"Report merged and saved to s3://{self.s3_bucket}/{merged_report_path}"
        )
        return merged_report_path

    FOLDER_NAME_TIMESTAMP = "%Y-%m-%d_%H-%M-%S"

    def __get_timestamp_now(self):
        return datetime.now().strftime(self.FOLDER_NAME_TIMESTAMP)

    REPLACE_SYMBOLS = ["::", ".", "/"]
    REPLACE_TO = "-"
    TMP_REPORT_FOLDER = "/tmp/junitxml/{}.xml"

    def __get_pytest_xml_report_path(self, node_id: str) -> str:
        for symbol in self.REPLACE_SYMBOLS:
            node_id = node_id.replace(symbol, self.REPLACE_TO)

        return self.TMP_REPORT_FOLDER.format(node_id)
