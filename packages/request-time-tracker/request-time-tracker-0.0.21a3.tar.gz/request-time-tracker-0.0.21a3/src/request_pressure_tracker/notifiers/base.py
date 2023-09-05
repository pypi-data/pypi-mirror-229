from request_pressure_tracker.notifier_locks.base import BaseNotifierLock


class BaseNotifier:
    """
    Base class to notify external service with metric request spent in internal queue
    """

    def __init__(self, lock: BaseNotifierLock = None):
        self.lock = lock

    def notify_pressure(self, pressure: float) -> None:
        """
        Push exact value of time spent in queue
        :param pressure: float, amount of time, worker spent processing requests comparing to total time
        """
        raise NotImplementedError
