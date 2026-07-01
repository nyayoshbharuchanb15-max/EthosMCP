from __future__ import annotations

from typing import Any


class _Counter:
    def __init__(self, name: str, description: str, labelnames: list[str] | None = None) -> None:
        self.name = name
        self.description = description
        self.labelnames = labelnames or []
        self._value: float = 0.0
        self._labels: dict[tuple, float] = {}

    def labels(self, **labels: str) -> _CounterLabels:
        return _CounterLabels(self, labels)

    def inc(self, amount: float = 1.0) -> None:
        self._value += amount

    def _inc_labels(self, labels: dict[str, str], amount: float = 1.0) -> None:
        key = tuple(sorted(labels.items()))
        self._labels[key] = self._labels.get(key, 0.0) + amount


class _CounterLabels:
    def __init__(self, counter: _Counter, labels: dict[str, str]) -> None:
        self._counter = counter
        self._labels = labels

    def inc(self, amount: float = 1.0) -> None:
        self._counter._inc_labels(self._labels, amount)


class _Histogram:
    def __init__(self, name: str, description: str, labelnames: list[str] | None = None, buckets: list[float] | None = None) -> None:
        self.name = name
        self.description = description
        self.labelnames = labelnames or []
        self.buckets = buckets or [0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0, float("inf")]
        self._values: list[float] = []

    def labels(self, **labels: str) -> _HistogramLabels:
        return _HistogramLabels(self, labels)

    def observe(self, value: float) -> None:
        self._values.append(value)


class _HistogramLabels:
    def __init__(self, histogram: _Histogram, labels: dict[str, str]) -> None:
        self._histogram = histogram
        self._labels = labels

    def observe(self, value: float) -> None:
        self._histogram._values.append(value)


class _Gauge:
    def __init__(self, name: str, description: str, labelnames: list[str] | None = None) -> None:
        self.name = name
        self.description = description
        self.labelnames = labelnames or []
        self._value: float = 0.0

    def labels(self, **labels: str) -> _GaugeLabels:
        return _GaugeLabels(self, labels)

    def set(self, value: float) -> None:
        self._value = value

    def inc(self, amount: float = 1.0) -> None:
        self._value += amount

    def dec(self, amount: float = 1.0) -> None:
        self._value -= amount


class _GaugeLabels:
    def __init__(self, gauge: _Gauge, labels: dict[str, str]) -> None:
        self._gauge = gauge
        self._labels = labels

    def set(self, value: float) -> None:
        self._gauge._value = value

    def inc(self, amount: float = 1.0) -> None:
        self._gauge._value += amount

    def dec(self, amount: float = 1.0) -> None:
        self._gauge._value -= amount


_USE_PROMETHEUS_CLIENT = False
try:
    from prometheus_client import Counter, Histogram, Gauge  # noqa: F401
    _USE_PROMETHEUS_CLIENT = True
except ImportError:
    pass


class MetricsCollector:
    def __init__(self) -> None:
        if _USE_PROMETHEUS_CLIENT:
            self._init_prometheus()
        else:
            self._init_fallback()

    def _init_prometheus(self) -> None:
        from prometheus_client import Counter, Histogram

        self.phase_duration = Histogram(
            "audit_phase_duration_seconds",
            "Duration of audit phases in seconds",
            labelnames=["phase", "status"],
            buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0, 600.0, float("inf")],
        )
        self.findings_severity = Counter(
            "audit_findings_by_severity_total",
            "Total number of findings by severity",
            labelnames=["severity", "phase"],
        )
        self.certificates_issued = Counter(
            "audit_certificates_issued_total",
            "Total number of certificates issued",
            labelnames=["status"],
        )
        self.drift_alerts = Counter(
            "audit_drift_alerts_total",
            "Total number of drift alerts triggered",
            labelnames=["severity", "metric"],
        )

    def _init_fallback(self) -> None:
        self.phase_duration = _Histogram(
            "audit_phase_duration_seconds",
            "Duration of audit phases in seconds",
            labelnames=["phase", "status"],
        )
        self.findings_severity = _Counter(
            "audit_findings_by_severity_total",
            "Total number of findings by severity",
            labelnames=["severity", "phase"],
        )
        self.certificates_issued = _Counter(
            "audit_certificates_issued_total",
            "Total number of certificates issued",
            labelnames=["status"],
        )
        self.drift_alerts = _Counter(
            "audit_drift_alerts_total",
            "Total number of drift alerts triggered",
            labelnames=["severity", "metric"],
        )

    def record_phase_duration(self, phase: str, duration_seconds: float, status: str = "completed") -> None:
        self.phase_duration.labels(phase=phase, status=status).observe(duration_seconds)

    def record_finding_severity(self, severity: str, phase: str, count: int = 1) -> None:
        for _ in range(count):
            self.findings_severity.labels(severity=severity, phase=phase).inc()

    def record_certificate_issued(self, status: str = "issued") -> None:
        self.certificates_issued.labels(status=status).inc()

    def record_drift_alert(self, severity: str, metric: str) -> None:
        self.drift_alerts.labels(severity=severity, metric=metric).inc()

    def collect_metrics(self) -> dict[str, Any]:
        return {
            "phase_duration": {
                "type": "histogram",
                "name": "audit_phase_duration_seconds",
                "help": "Duration of audit phases in seconds",
            },
            "findings_by_severity": {
                "type": "counter",
                "name": "audit_findings_by_severity_total",
                "help": "Total number of findings by severity",
            },
            "certificates_issued": {
                "type": "counter",
                "name": "audit_certificates_issued_total",
                "help": "Total number of certificates issued",
            },
            "drift_alerts": {
                "type": "counter",
                "name": "audit_drift_alerts_total",
                "help": "Total number of drift alerts triggered",
            },
        }

    def generate_metrics_text(self) -> str:
        lines: list[str] = []
        lines.append("# HELP audit_phase_duration_seconds Duration of audit phases in seconds")
        lines.append("# TYPE audit_phase_duration_seconds histogram")
        if isinstance(self.phase_duration, _Histogram):
            lines.append(f"audit_phase_duration_seconds_count {len(self.phase_duration._values)}")
            if self.phase_duration._values:
                lines.append(f"audit_phase_duration_seconds_sum {sum(self.phase_duration._values)}")
        else:
            lines.append("audit_phase_duration_seconds_count 0")
            lines.append("audit_phase_duration_seconds_sum 0")

        lines.append("")
        lines.append("# HELP audit_findings_by_severity_total Total number of findings by severity")
        lines.append("# TYPE audit_findings_by_severity_total counter")
        if isinstance(self.findings_severity, _Counter):
            for key, val in self.findings_severity._labels.items():
                labels_str = ",".join(f'{k}="{v}"' for k, v in key)
                lines.append(f'audit_findings_by_severity_total{{{labels_str}}} {int(val)}')
            lines.append(f'audit_findings_by_severity_total {int(self.findings_severity._value)}')

        lines.append("")
        lines.append("# HELP audit_certificates_issued_total Total number of certificates issued")
        lines.append("# TYPE audit_certificates_issued_total counter")
        if isinstance(self.certificates_issued, _Counter):
            for key, val in self.certificates_issued._labels.items():
                labels_str = ",".join(f'{k}="{v}"' for k, v in key)
                lines.append(f'audit_certificates_issued_total{{{labels_str}}} {int(val)}')
            lines.append(f'audit_certificates_issued_total {int(self.certificates_issued._value)}')

        lines.append("")
        lines.append("# HELP audit_drift_alerts_total Total number of drift alerts triggered")
        lines.append("# TYPE audit_drift_alerts_total counter")
        if isinstance(self.drift_alerts, _Counter):
            for key, val in self.drift_alerts._labels.items():
                labels_str = ",".join(f'{k}="{v}"' for k, v in key)
                lines.append(f'audit_drift_alerts_total{{{labels_str}}} {int(val)}')
            lines.append(f'audit_drift_alerts_total {int(self.drift_alerts._value)}')

        return "\n".join(lines)
