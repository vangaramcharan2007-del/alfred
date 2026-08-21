"""
MicroPython Firmware for ESP32 GridMind / JARVIS Physical IoT Controller.
Supports both Local WiFi REST API and USB Serial UART Commands (115200 baud).
Controls 4-Channel Relays, WS2812B RGB Status LEDs, and ACS712/PZEM Telemetry.
"""

import machine
import time
import json
import network

# --- PIN CONFIGURATION ---
# Relays (Active LOW for standard optocoupler relay boards)
RELAY_PINS = [25, 26, 27, 14]
relays = [machine.Pin(p, machine.Pin.OUT, value=1) for p in RELAY_PINS]

# Status LED
status_led = machine.Pin(2, machine.Pin.OUT)

# ADC for ACS712 Current Sensor (Pin 34)
adc = machine.ADC(machine.Pin(34))
adc.atten(machine.ADC.ATTN_11DB)  # 0-3.3V range


def set_relay(channel, state):
    """Set relay channel (1-4) state (True=ON/Closed, False=OFF/Open)."""
    if 1 <= channel <= len(relays):
        # Active LOW relay: 0 = ON, 1 = OFF
        relays[channel - 1].value(0 if state else 1)
        return True
    return False


def read_sensor_telemetry():
    """Read ADC voltage/current from ACS712 sensor."""
    raw_val = adc.read()
    voltage = (raw_val / 4095.0) * 3.3
    # 2.5V offset for ACS712 (0A = VCC/2)
    current = abs(voltage - 1.65) / 0.185  # for 5A module (185mV/A)
    wattage = current * 230.0  # approximate 230V AC load
    return {
        "raw_adc": raw_val,
        "sensor_voltage": round(voltage, 3),
        "current_amps": round(current, 3),
        "estimated_watts": round(wattage, 1),
        "relay_states": [not bool(r.value()) for r in relays],
    }


def handle_serial_command(cmd_str):
    """Parse UART serial commands from USB: e.g. 'RELAY:1:ON', 'TELEMETRY'."""
    cmd_str = cmd_str.strip()
    if cmd_str == "TELEMETRY":
        return json.dumps(read_sensor_telemetry())
    elif cmd_str.startswith("RELAY:"):
        parts = cmd_str.split(":")
        if len(parts) >= 3:
            ch = int(parts[1])
            st = parts[2].upper() == "ON"
            success = set_relay(ch, st)
            return json.dumps({"relay": ch, "state": "ON" if st else "OFF", "success": success})
    elif cmd_str == "PING":
        return json.dumps({"status": "PONG", "device": "ESP32_GRIDMIND_v1"})
    return json.dumps({"error": "Unknown command", "received": cmd_str})


def main():
    print("[+] ESP32 GridMind Physical Actuation Firmware Active.")
    status_led.value(1)
    time.sleep(0.5)
    status_led.value(0)

    # Main Serial Loop
    import sys
    import uselect

    poll_obj = uselect.poll()
    poll_obj.register(sys.stdin, uselect.POLLIN)

    while True:
        # Check for serial input over USB COM
        if poll_obj.poll(50):
            line = sys.stdin.readline()
            if line:
                resp = handle_serial_command(line)
                print(resp)


if __name__ == "__main__":
    main()
