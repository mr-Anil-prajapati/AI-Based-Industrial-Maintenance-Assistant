from __future__ import annotations


class MachineAnalyzer:
    def analyze(self, question: str, signals: dict[str, object]) -> dict[str, object]:
        normalized = question.lower()
        if "motor" in normalized:
            return self._motor_analysis(signals)
        if "compressor" in normalized:
            return self._compressor_analysis(signals)
        if "conveyor" in normalized:
            return self._conveyor_analysis(signals)
        return self._generic_analysis(signals)

    def _motor_analysis(self, signals: dict[str, object]) -> dict[str, object]:
        checks: list[str] = []
        if not signals.get("run_feedback") and signals.get("start_command"):
            checks.append("Motor has a start demand but no run feedback.")
        if not signals.get("safety_interlock_ok"):
            checks.append("Safety interlock is not satisfied.")
        if signals.get("overload_trip"):
            checks.append("Overload relay is tripped.")
        if signals.get("emergency_stop"):
            checks.append("Emergency stop chain is active.")
        likely_causes = [
            cause
            for cause in (
                "Safety interlock open" if not signals.get("safety_interlock_ok") else None,
                "Overload relay trip" if signals.get("overload_trip") else None,
                "Emergency stop active" if signals.get("emergency_stop") else None,
                "No start permissive feedback" if not signals.get("run_feedback") else None,
            )
            if cause
        ]
        return {"asset_type": "motor", "checks": checks, "likely_causes": likely_causes, "signals": signals}

    def _compressor_analysis(self, signals: dict[str, object]) -> dict[str, object]:
        checks = []
        if float(signals.get("temperature_c", 0.0)) > 90.0:
            checks.append("Measured temperature exceeds normal operating band.")
        if signals.get("high_temp_alarm"):
            checks.append("High temperature alarm is active.")
        return {
            "asset_type": "compressor",
            "checks": checks,
            "likely_causes": [
                "Insufficient cooling airflow",
                "Dirty heat exchanger",
                "High discharge pressure",
            ],
            "signals": signals,
        }

    def _conveyor_analysis(self, signals: dict[str, object]) -> dict[str, object]:
        checks = []
        if signals.get("jam_detected"):
            checks.append("Jam sensor indicates material blockage.")
        if signals.get("overload_trip"):
            checks.append("Conveyor overload trip is active.")
        return {
            "asset_type": "conveyor",
            "checks": checks,
            "likely_causes": ["Mechanical jam", "Motor overload", "Downstream blockage"],
            "signals": signals,
        }

    def _generic_analysis(self, signals: dict[str, object]) -> dict[str, object]:
        return {
            "asset_type": "generic",
            "checks": ["Review active alarms and compare command versus feedback signals."],
            "likely_causes": list(signals.get("alarm_bits", [])),
            "signals": signals,
        }
