# Installation guide

## 1) Bridge addon
Make sure the Python bridge addon is installed and running.

Important repo files:
- `cs2_gsi_bridge_py/app/main.py`
- `cs2_gsi_bridge_py/config.yaml`
- `cs2_gsi_bridge_py/Dockerfile`
- `cs2_gsi_bridge_py/run.sh`

## 2) Enable Home Assistant packages
In `configuration.yaml`:

```yaml
homeassistant:
  packages: !include_dir_named packages
```

Then create:
- `/config/packages/`

Copy:
- `home_assistant/packages/cs2_tvled_package.yaml`

into that folder.

## 3) Find your TV LED light entity
Go to:
- Developer Tools -> States

Search:
- `light.`

Find your TV LED light entity, for example:
- `light.cozylife_8nqa_light_2`

Then replace every:
- `light.YOUR_TVLED_ENTITY`

with your real entity ID.

## 4) Verify your bridge entity IDs
Go to:
- Developer Tools -> States

Search:
- `cs2_gsi_bridge`

Most setups use IDs like:
- `sensor.cs2_gsi_bridge_cs2_gsi_bridge_round_phase`
- `sensor.cs2_gsi_bridge_cs2_gsi_bridge_round_bomb`
- `sensor.cs2_gsi_bridge_cs2_gsi_bridge_player_team`
- `sensor.cs2_gsi_bridge_cs2_gsi_bridge_player_state_health`
- `sensor.cs2_gsi_bridge_cs2_gsi_bridge_player_state_flashed`
- `sensor.cs2_gsi_bridge_cs2_gsi_bridge_player_state_burning`
- `sensor.cs2_gsi_bridge_cs2_gsi_bridge_player_state_smoked`
- `sensor.cs2_gsi_bridge_cs2_gsi_bridge_light_mode`
- `sensor.cs2_gsi_bridge_cs2_gsi_bridge_light_color`
- `binary_sensor.cs2_gsi_bridge_cs2_gsi_bridge_light_pulse`

If your IDs differ, do a global search/replace in the package file.

## 5) Reload Home Assistant
After placing the package:
- restart Home Assistant
or
- reload YAML where applicable

## 6) Expected behavior
- Bomb planted: red blink, perceived beep aligned
- Bomb exploded: 5s red hold
- Bomb defused: blue blink
- Freezetime: full team color
- Live round: dim team color
- Flash: white overlay, then restore
- Burning: orange/red flicker
- Smoke: dim team color
- Low HP 16-29: dim team-color breathing (5% to 35%)
- Critical HP 1-15: red breathing (5% to 100%)
- Damage: short boost, then restore

## Optional: disable Low HP only
If you do not want low HP effects, disable:
- `CS2 Bridge - Low HP Controller TVLED`
- `CS2 Bridge - Damage kurzer Boost TVLED`

This keeps team-color, smoke, burning, flash, bomb, and restore behavior.

## Notes
- The bomb blink is intentionally inverted on the Home Assistant side:
  - `light_pulse = off` -> lamp ON
  - `light_pulse = on` -> lamp OFF
  This matched the perceived bomb beep timing best.
- Smoke is designed to be more visible than the normal live-round base color.
- Bombtimer has priority and should not be edited casually once it is working.
