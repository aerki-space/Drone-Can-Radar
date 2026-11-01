# DroneCAN interface

The radar is a DroneCAN (UAVCAN v0) node on the vehicle's CAN bus.

## Node behaviour

| Item | Behaviour |
|---|---|
| Node ID | Dynamic allocation by default; fixed ID via the `NODE_ID` parameter |
| `uavcan.protocol.NodeStatus` | 1 Hz. Health goes to WARNING on over-temperature or low supply, and ERROR on RF fault. Mode is OPERATIONAL while transmitting. |
| `uavcan.protocol.GetNodeInfo` | Name `com.aerki.radar24`, hardware and software versions, unique ID |
| `uavcan.protocol.param.GetSet` / `ExecuteOpcode` | All configuration (table below), stored in flash |
| `uavcan.protocol.RestartNode` | Supported |
| `uavcan.protocol.file.BeginFirmwareUpdate` | Bootloader update over CAN (planned) |

## Published messages

| Message | ID | Rate | Content |
|---|---|---|---|
| `uavcan.equipment.range_sensor.Measurement` | 1050 (standard) | Each scan (or frame in fixed mode) | Nearest valid return within ±`RNG_CONE` of boresight, `sensor_type = RADAR` |
| `aerki.radar.Detections` | 20400 (vendor) | Each frame, capped by `PUB_MAX_HZ` | Beam direction plus up to 16 targets (range, az, el, radial velocity, SNR) |
| `aerki.radar.Status` | 20401 (vendor) | 1 Hz | Mode, TX state, temperature, supply, frame rate, error flags |

## Services

| Service | ID | Purpose |
|---|---|---|
| `aerki.radar.SetBeam` | 210 (vendor) | Standby, hold a fixed direction, or resume scanning |

The definitions are in [`../dsdl/aerki/radar/`](../dsdl/aerki/radar/). `python3 tools/validate_dsdl.py` parses them
with the DroneCAN parser and prints sizes and signatures. Before release, confirm the vendor IDs don't collide with
other vendor-specific types on the same bus.

## Bus load

A full `Detections` message (16 targets) is 175 bytes. On classic CAN that's a multi-frame transfer of about 26
frames, or roughly 3.5 ms of a 1 Mbit/s bus.
- **Classic CAN:** `PUB_MAX_HZ` defaults to 20, which is about 7 % bus load in the worst case and much less in
  practice, because most frames carry few targets. Detections from frames in between are merged and keep the
  strongest.
- **CAN FD:** if the flight controller and bus support it, this drops by roughly 8× and per-frame publishing
  becomes practical.

## Parameters

| Name | Default | Meaning |
|---|---|---|
| `NODE_ID` | 0 | 0 = dynamic allocation |
| `SENSOR_ID` | 0 | Copied into the vendor messages to tell several radars apart |
| `TX_EN` | 0 | Transmitter enable. **Off by default, so the radar never radiates on the bench unexpectedly.** |
| `SCAN_AZ_MIN` / `SCAN_AZ_MAX` / `SCAN_AZ_STEP` | −45 / 45 / 15 | deg |
| `SCAN_EL_MIN` / `SCAN_EL_MAX` / `SCAN_EL_STEP` | 0 / 0 / 15 | deg (a single row by default) |
| `RNG_MIN` / `RNG_MAX` | 1.5 / 90 | m, valid range window (the minimum gates out propeller returns) |
| `RNG_CONE` | 10 | deg, half-angle used for the standard range-sensor message |
| `CFAR_SNR` | 13 | dB, detection threshold |
| `PUB_MAX_HZ` | 20 | Hz, cap on the `Detections` rate |
| `MOUNT_YAW` / `MOUNT_PITCH` / `MOUNT_ROLL` | 0 | deg, sensor orientation on the airframe (reported, not applied) |

## Flight-controller integration

- **ArduPilot, today:** enable DroneCAN on the CAN port. Set a rangefinder to the DroneCAN type, with an address
  matching the node's sensor ID. The radar then works as a forward or downward rangefinder through the standard
  `range_sensor.Measurement` message, with no flight-controller changes.
- **ArduPilot proximity / avoidance:** this needs a small driver that turns `aerki.radar.Detections` into
  proximity sectors. ArduPilot also defines its own DroneCAN proximity message; publishing that as well may avoid a
  custom driver. Check the current ArduPilot DSDL before choosing.
- **PX4:** also supports DroneCAN peripherals, including rangefinders through the standard `range_sensor.Measurement`
  message, once the rangefinder subscription is enabled in its UAVCAN parameters. The vendor `Detections` message
  would need a PX4 driver.
- **Ground tools:** the DroneCAN GUI tool can set parameters, call `SetBeam` and plot detections once
  `dsdl/aerki` is added to its custom DSDL path.
