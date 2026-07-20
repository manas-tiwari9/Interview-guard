import time


class BehaviourTracker:
    """
    Tracks one behaviour type over time.
    State machine: NORMAL → OBSERVATION → SUSPICIOUS → WARNING → VIOLATION
    Cooldown prevents brief absences (< 1s) from resetting the timer.
    """

    def __init__(self, thresholds: dict, cooldown: float = 1.0):
        self.thresholds = thresholds
        self.cooldown   = cooldown
        self.state      = "NORMAL"
        self.elapsed    = 0.0
        self._onset     = None   # when the condition first turned active
        self._last_seen = None   # last frame the condition was True

    def observe(self, is_active: bool, now: float):
        """
        Feed one frame.
        Returns "ESCALATED", "CLEARED", or None.
        """
        if is_active:
            self._last_seen = now
            if self._onset is None:
                self._onset = now

            self.elapsed  = now - self._onset
            new_state     = self._compute(self.elapsed)

            if new_state != self.state:
                self.state = new_state
                return "ESCALATED"

        else:
            if self._last_seen is not None and (now - self._last_seen) >= self.cooldown:
                prev        = self.state
                self.state  = "NORMAL"
                self.elapsed = 0.0
                self._onset  = None
                self._last_seen = None
                if prev != "NORMAL":
                    return "CLEARED"

        return None

    def _compute(self, elapsed: float) -> str:
        t = self.thresholds
        if elapsed >= t.get("violation",  float("inf")): return "VIOLATION"
        if elapsed >= t.get("warning",    float("inf")): return "WARNING"
        if elapsed >= t.get("suspicious", float("inf")): return "SUSPICIOUS"
        if elapsed >= t.get("observation",float("inf")): return "OBSERVATION"
        return "NORMAL"
