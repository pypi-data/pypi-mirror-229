class BaseNotifierLock:
    def __init__(self, lock_name: str):
        self.lock_name = lock_name

    def lock(self) -> bool:
        raise NotImplementedError

    def unlock(self):
        raise NotImplementedError
