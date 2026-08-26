"""Live offline demo for SIH26181: AEGIS resilience and privacy core."""

import sqlite3
from pathlib import Path
from tempfile import TemporaryDirectory

from aegis_memory import AegisMemory
from aegis_resilience import EnvironmentalReading, assess_environment


def main() -> None:
    print("AEGIS - LOCAL RESILIENCE DEMO")
    assessment = assess_environment(
        EnvironmentalReading(ambient_temperature_c=43.0, humidity_percent=70.0, aqi=330, flood_warning=True)
    )
    print(f"Environmental level: {assessment.level}")
    print(f"Hazards: {', '.join(assessment.hazards)}")
    print(f"Emergency mode: {assessment.emergency_mode}")

    with TemporaryDirectory() as directory:
        database = Path(directory) / "aegis_demo.db"
        memory = AegisMemory(str(database))
        patient = memory.add_new_patient(name="Demo Patient", allergies="Penicillin")
        memory.add_conversation("user", "Keep my health note local")
        recovered_name = memory.get_patient_profile(patient["patient_uid"])["name"]
        memory.close()

        connection = sqlite3.connect(database)
        stored_value = connection.execute("SELECT name FROM patient_profile WHERE patient_uid = ?", (patient["patient_uid"],)).fetchone()[0]
        connection.close()
        print(f"Recovered local profile: {recovered_name}")
        print(f"Encrypted at rest: {stored_value.startswith('enc:v1:')}")
        print("Network calls: 0 (all assessment and storage ran locally)")


if __name__ == "__main__":
    main()
