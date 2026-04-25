# Changelog

## Final
- stabilized CS2 -> MQTT -> Home Assistant pipeline
- added full-state MQTT publishing for incoming GSI leaves
- added derived light entities:
  - `light_mode`
  - `light_color`
  - `light_pulse`
  - `blink_interval_ms`
- tuned bomb blink so perceived light timing matches the beep better
- removed special end-finale override and kept fast blink behavior to explosion
- added 5-second solid red explosion hold
- added blue defuse blink effect
- added full team-color freeze time
- added dim team-color live round behavior
- added smoke dim team-color overlay
- added flash overlay with restore-context behavior
- added burning flicker effect
- added low HP breathing effects
- added critical HP red breathing
- added restore-context script so temporary overlays return to the correct active state
- ensured bomb timer remains highest priority and is not broken by overlays

## Earlier iterations
- initial bridge build for HA OS
- Dockerfile fixes for addon build
- MQTT discovery fixes
- pulse publishing fixes
- bomb timing refinements
- multiple HA priority and restore logic passes
