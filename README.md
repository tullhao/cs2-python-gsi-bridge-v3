# CS2 GSI Bridge (Python Full State) + Home Assistant TVLED

A Counter-Strike 2 Game State Integration bridge for Home Assistant that publishes CS2 state over MQTT and drives a TV LED with game-aware effects.

## What this project does

This setup connects **CS2 -> Python GSI Bridge -> MQTT -> Home Assistant -> TV LED** and gives you:

- bomb timer blink synced to the bomb beep
- bomb exploded hold-red effect
- bomb defused blue blink effect
- freeze time full team color
- live round dimmed team color
- smoke dim team color
- flashed white overlay with clean restore
- burning orange/red flicker
- low HP breathing effects
- full-state MQTT publishing for all incoming GSI leaf states

## Current final behavior

### Bomb
- **Bomb planted**: red blink, matched to the perceived beep timing
- **Bomb exploded**: solid red for 5 seconds, then restore context
- **Bomb defused**: blue blink effect, then restore context

### Team / round state
- **Freezetime**:
  - CT = full blue
  - T = full green
- **Live round**:
  - CT = dim blue
  - T = dim green

### Player state overlays
- **Flash**: white overlay, then restore previous context
- **Burning**: orange/red flicker
- **Smoke**: dimmed team color
- **Low HP 16-29**: team color breathing
- **Critical HP 1-15**: red breathing
- **Damage**: short boost, then restore context

## Architecture

- **Bridge addon**: receives CS2 GSI HTTP posts
- **MQTT**: publishes raw and derived state
- **Home Assistant automations/scripts**: map game state to TV LED behavior

## MQTT entities of interest

Important derived entities:

- `sensor.cs2_gsi_bridge_cs2_gsi_bridge_light_mode`
- `sensor.cs2_gsi_bridge_cs2_gsi_bridge_light_color`
- `binary_sensor.cs2_gsi_bridge_cs2_gsi_bridge_light_pulse`
- `sensor.cs2_gsi_bridge_cs2_gsi_bridge_round_bomb`
- `sensor.cs2_gsi_bridge_cs2_gsi_bridge_round_phase`
- `sensor.cs2_gsi_bridge_cs2_gsi_bridge_player_team`
- `sensor.cs2_gsi_bridge_cs2_gsi_bridge_player_state_health`
- `sensor.cs2_gsi_bridge_cs2_gsi_bridge_player_state_flashed`
- `sensor.cs2_gsi_bridge_cs2_gsi_bridge_player_state_burning`
- `sensor.cs2_gsi_bridge_cs2_gsi_bridge_player_state_smoked`

## Required Home Assistant scripts

Final script set:

- `CS2 Bridge - Apply TVLED State`
- `CS2 Bridge - Restore Context TVLED`
- `CS2 Bridge - Burning Flicker TVLED`
- `CS2 Bridge - Low HP Team Breath TVLED`
- `CS2 Bridge - Critical HP Red Breath TVLED`
- `CS2 Bridge - Defused Blue Blink TVLED`

## Required Home Assistant automations

Final automation set:

- `CS2 Bridge - Apply TVLED State on Change`
- `CS2 Bridge - Bombtimer einzig TVLED`
- `CS2 Bridge - Bomb exploded rot kurz TVLED`
- `CS2 Bridge - Bomb defused blau blinken TVLED`
- `CS2 Bridge - Burning Start TVLED`
- `CS2 Bridge - Burning Ende TVLED`
- `CS2 Bridge - Flashed kurzer Flash TVLED`
- `CS2 Bridge - Low HP Controller TVLED`
- `CS2 Bridge - Damage kurzer Boost TVLED`

Keep this one disabled or removed:

- `CS2 Bridge - Bombtimer Ende Licht aus TVLED`

## Optional: disable Low HP only

If you want to disable Low HP effects while keeping team color, bomb logic, flash, smoke, and burning, do it as a proper feature toggle on the HA side rather than only disabling one random automation.

Recommended Low HP related components are:

- `CS2 Bridge - Low HP Controller TVLED`
- `CS2 Bridge - Damage kurzer Boost TVLED`
- `CS2 Bridge - Low HP Team Breath TVLED`
- `CS2 Bridge - Critical HP Red Breath TVLED`

## Repo structure

- `cs2_gsi_bridge_py/app/main.py`
- `cs2_gsi_bridge_py/config.yaml`
- `cs2_gsi_bridge_py/Dockerfile`
- `cs2_gsi_bridge_py/run.sh`

## Notes

- Bomb blink perception is intentionally inverted on the HA side so the lamp lights on the beep moment.
- The bridge stays responsible for pulse timing.
- Home Assistant is responsible for visible lamp behavior and state priority.

## Status

This is the current final working setup as tuned in Home Assistant.
