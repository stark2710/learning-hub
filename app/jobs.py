class JobRegistry:
    _store: dict = {}

    @classmethod
    def get(cls, job_id: str) -> dict:
        return cls._store.get(job_id, {"status": "not_found"})

    @classmethod
    def set(cls, job_id: str, data: dict) -> None:
        cls._store[job_id] = data
