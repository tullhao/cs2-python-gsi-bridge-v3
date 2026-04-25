# CS2 GSI Bridge (Python Full State) + Home Assistant TVLED

A Counter-Strike 2 Game State Integration bridge for Home Assistant that publishes CS2 state over MQTT and drives a TV LED with game-aware effects.

## Included in this repo bundle
- addon bridge README
- changelog
- features overview
- MIT license
- complete Home Assistant package
- setup guide explaining which entity IDs must be checked and adjusted

## Final effect set
### Bomb
- Bomb planted: red blink synced to the perceived beep
- Bomb exploded: solid red for 5 seconds
- Bomb defused: blue blink effect

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

## Files
- `home_assistant/packages/cs2_tvled_package.yaml`
- `docs/INSTALL_GUIDE.md`
- `README.md`
- `CHANGELOG.md`
- `FEATURES.md`
- `LICENSE`
