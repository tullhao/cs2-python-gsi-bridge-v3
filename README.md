# CS2 GSI Bridge (Python Full State) + Home Assistant TVLED

This repo contains:
- the Home Assistant add-on bridge
- a ready-to-import Home Assistant package
- manual YAML helper files
- a CS2 GSI config example
- setup documentation

## Final intended effects
### Bomb
- Bomb planted: red blink synced to the perceived beep
- Bomb exploded: solid red for 5 seconds
- Bomb defused: blue blink

### Team / round state
- Freezetime:
  - CT = full blue
  - T = full green
- Live round:
  - CT = dim blue
  - T = dim green

### Player overlays
- Flash: white overlay, then restore
- Burning: orange/red flicker
- Smoke: dim team color
- Low HP 16-29: dim team-color breathing (5% to 35%)
- Critical HP 1-15: red breathing (5% to 100%)
- Damage: short boost, then restore

## Important docs
- docs/INSTALL_GUIDE.md
- docs/ENTITY_CHECKLIST.md
- docs/CS2_CONFIG.md
