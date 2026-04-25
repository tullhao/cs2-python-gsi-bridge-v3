# Entity checklist

## Light entity
Replace all:
- light.YOUR_TVLED_ENTITY

with your actual TV LED light entity.

## Bridge entities to verify
Search in Home Assistant Developer Tools -> States for:
- cs2_gsi_bridge

Common IDs:
- sensor.cs2_gsi_bridge_cs2_gsi_bridge_round_phase
- sensor.cs2_gsi_bridge_cs2_gsi_bridge_round_bomb
- sensor.cs2_gsi_bridge_cs2_gsi_bridge_player_team
- sensor.cs2_gsi_bridge_cs2_gsi_bridge_player_state_health
- sensor.cs2_gsi_bridge_cs2_gsi_bridge_player_state_flashed
- sensor.cs2_gsi_bridge_cs2_gsi_bridge_player_state_burning
- sensor.cs2_gsi_bridge_cs2_gsi_bridge_player_state_smoked
- sensor.cs2_gsi_bridge_cs2_gsi_bridge_light_mode
- sensor.cs2_gsi_bridge_cs2_gsi_bridge_light_color
- binary_sensor.cs2_gsi_bridge_cs2_gsi_bridge_light_pulse
