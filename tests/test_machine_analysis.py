from backend.machine_analysis.rules import MachineAnalyzer


def test_motor_analysis_detects_interlock_issue():
    analyzer = MachineAnalyzer()
    result = analyzer.analyze(
        "Why is Motor-1 not running?",
        {
            "run_feedback": False,
            "start_command": True,
            "safety_interlock_ok": False,
            "overload_trip": False,
            "emergency_stop": False,
            "alarm_bits": ["MTR01_INTERLOCK"],
        },
    )

    assert result["asset_type"] == "motor"
    assert "Safety interlock open" in result["likely_causes"]
    assert any("start demand" in item.lower() for item in result["checks"])
