import time


class Tick:
    _start = 0
    _end = 0
    _waiting_start = 0
    _waiting_time = 0

    @staticmethod
    def start() -> float:
        """Start the timer.

        Returns:
            float: The start time.
        """
        Tick._start = time.perf_counter()
        Tick._waiting_time = 0
        return Tick._start

    @staticmethod
    def stop() -> float:
        """Stop the timer.

        Returns:
            float: The stop time.
        """
        Tick._end = time.perf_counter()
        return Tick._end

    @staticmethod
    def get_seconds() -> float:
        """Get the seconds that elapsed between start and end.

        Returns:
            float: The total number of seconds.
        """
        return Tick._end - Tick._start

    @staticmethod
    def get_active_seconds() -> float:
        """Get the real seconds between start and end without waiting.

        Returns:
            float: The total number of seconds.
        """
        return (Tick._end - Tick._start) - Tick._waiting_time

    @staticmethod
    def wait() -> None:
        """Pause the timer."""
        Tick._waiting_start = time.perf_counter()

    @staticmethod
    def stop_waiting() -> None:
        """Resume the timer after waiting."""
        if Tick._waiting_start:
            Tick._waiting_time += time.perf_counter() - Tick._waiting_start
            Tick._waiting_start = 0
