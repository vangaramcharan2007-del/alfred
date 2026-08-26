"""Deterministic, offline environmental-health risk assessment for AEGIS.

This module deliberately uses transparent thresholds rather than claiming a
clinically validated diagnostic model. It runs with no network dependency.
"""

from dataclasses import asdict, dataclass
from typing import Dict, List, Optional


@dataclass(frozen=True)
class EnvironmentalReading:
    ambient_temperature_c: Optional[float] = None
    humidity_percent: Optional[float] = None
    aqi: Optional[int] = None
    flood_warning: bool = False


@dataclass(frozen=True)
class EnvironmentalAssessment:
    level: str
    heat_index_c: Optional[float]
    hazards: List[str]
    recommendations: List[str]
    emergency_mode: bool

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


def _heat_index_c(temperature_c: float, humidity_percent: float) -> float:
    """Return a NOAA-style heat-index approximation in Celsius."""
    fahrenheit = (temperature_c * 9 / 5) + 32
    relative_humidity = humidity_percent
    if fahrenheit < 80 or relative_humidity < 40:
        return round(temperature_c, 1)
    index_f = (
        -42.379
        + 2.04901523 * fahrenheit
        + 10.14333127 * relative_humidity
        - 0.22475541 * fahrenheit * relative_humidity
        - 0.00683783 * fahrenheit**2
        - 0.05481717 * relative_humidity**2
        + 0.00122874 * fahrenheit**2 * relative_humidity
        + 0.00085282 * fahrenheit * relative_humidity**2
        - 0.00000199 * fahrenheit**2 * relative_humidity**2
    )
    return round((index_f - 32) * 5 / 9, 1)


def assess_environment(reading: EnvironmentalReading) -> EnvironmentalAssessment:
    """Assess heat, air-quality and flood risks using locally supplied values."""
    hazards: List[str] = []
    recommendations: List[str] = []
    heat_index = None

    if reading.ambient_temperature_c is not None and reading.humidity_percent is not None:
        heat_index = _heat_index_c(reading.ambient_temperature_c, reading.humidity_percent)
        if heat_index >= 54:
            hazards.append("EXTREME_HEAT_STRESS")
            recommendations.append("Move to shade or cooling now; begin oral rehydration and seek help for confusion or fainting.")
        elif heat_index >= 41:
            hazards.append("HIGH_HEAT_STRESS")
            recommendations.append("Avoid exertion, hydrate, and take a cooling break within 15 minutes.")
        elif heat_index >= 32:
            hazards.append("MODERATE_HEAT_STRESS")
            recommendations.append("Hydrate regularly and reduce prolonged outdoor activity.")

    if reading.aqi is not None:
        if reading.aqi > 300:
            hazards.append("SEVERE_AIR_QUALITY")
            recommendations.append("Stay indoors if possible; use a well-fitting mask if travel is essential.")
        elif reading.aqi > 200:
            hazards.append("VERY_POOR_AIR_QUALITY")
            recommendations.append("Limit exertion outdoors, especially for people with respiratory illness.")
        elif reading.aqi > 100:
            hazards.append("POOR_AIR_QUALITY")
            recommendations.append("Sensitive people should reduce extended outdoor activity.")

    if reading.flood_warning:
        hazards.append("FLOOD_DISRUPTION")
        recommendations.append("Keep medicines, drinking water, and charged emergency contacts ready; avoid floodwater.")

    if any(item in hazards for item in ("EXTREME_HEAT_STRESS", "SEVERE_AIR_QUALITY", "FLOOD_DISRUPTION")):
        level = "HIGH"
    elif hazards:
        level = "ELEVATED"
    else:
        level = "NORMAL"
        recommendations.append("No environmental hazard detected from the locally supplied readings.")

    return EnvironmentalAssessment(
        level=level,
        heat_index_c=heat_index,
        hazards=hazards,
        recommendations=recommendations,
        emergency_mode=reading.flood_warning or level == "HIGH",
    )
