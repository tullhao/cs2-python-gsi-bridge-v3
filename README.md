# CS2 Python GSI Bridge v3

This Home Assistant add-on receives Counter-Strike 2 Game State Integration (GSI)
HTTP POSTs on port 3001 and publishes:

- all incoming GSI leaf values under `cs2_bridge/state/...`
- MQTT discovery entities for all incoming leaf values
- derived helper entities:
  - `sensor.cs2_gsi_bridge_light_mode`
  - `sensor.cs2_gsi_bridge_light_color`
  - `binary_sensor.cs2_gsi_bridge_light_pulse`
  - `sensor.cs2_gsi_bridge_blink_interval_ms`
  - `sensor.cs2_gsi_bridge_bomb_countdown`
  - `sensor.cs2_gsi_bridge_bomb_state`
  - etc.

Important: this add-on exposes **everything CS2 actually sends**. It cannot invent
fields that Valve does not post for your current game mode / spectator state / cfg.
