import logging
import threading
from datetime import datetime

import boto3
from botocore.config import Config

from request_pressure_tracker.notifier_locks.base import BaseNotifierLock
from request_pressure_tracker.notifiers.base import BaseNotifier

logger = logging.getLogger('django.time_in_queue')


def notify_cloudwatch_pressure(
        access_key: str,
        secret_key: str,
        region: str,
        environment: str,
        pressure: float,
        lock: BaseNotifierLock = None,
) -> None:
    if lock is not None and not lock.lock():
        # lock not available, someone else is reporting
        return

    config = Config(connect_timeout=5, retries={'max_attempts': 0})
    client = boto3.client(
        'cloudwatch',
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region,
        config=config,
    )
    response = client.put_metric_data(
        Namespace='Custom',
        MetricData=[
            {
                'MetricName': 'RequestPressure',
                'Dimensions': [
                    {
                        'Name': 'Environment',
                        'Value': environment
                    },
                ],
                'Timestamp': datetime.utcnow(),
                'Value': pressure * 100,
                'Unit': 'Percent',
                'StorageResolution': 1,
            }
        ]
    )

    if lock is not None:
        lock.unlock()

    try:
        status_code = response['ResponseMetadata']['HTTPStatusCode']
    except KeyError:
        logger.warning('TimeInQueue export failing. Unable to find status code in response')
        return

    if status_code != 200:
        logger.warning('TimeInQueue export failing. Status code: {0}'.format(status_code))


class CloudWatchNotifier(BaseNotifier):
    def __init__(
            self,
            environment: str,
            aws_access_key: str,
            aws_secret_key: str,
            aws_region: str,
            lock: BaseNotifierLock = None,
    ):
        super().__init__(lock=lock)

        self.environment = environment
        self.aws_access_key = aws_access_key
        self.aws_secret_key = aws_secret_key
        self.aws_region = aws_region

        self.initialized = True
        if not all([
            isinstance(x, str)
            for x in [self.environment, self.aws_access_key, aws_secret_key, aws_region]
        ]):
            self.initialized = False
            logger.error('Cloudwatch notifier failed to be initialized: not all arguments are strings.')

    def notify_pressure(self, pressure: float) -> None:
        if not self.initialized:
            return

        threading.Thread(
            target=notify_cloudwatch_pressure,
            args=[
                self.aws_access_key, self.aws_secret_key, self.aws_region,
                self.environment, pressure,
            ],
            kwargs={
                'lock': self.lock,
            }
        ).start()
