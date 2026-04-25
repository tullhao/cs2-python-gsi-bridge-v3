# Complete installation guide

## Files to replace in GitHub
Replace these files:
- cs2_gsi_bridge_py/app/main.py
- cs2_gsi_bridge_py/config.yaml
- README.md
- CHANGELOG.md
- FEATURES.md
- docs/INSTALL_GUIDE.md
- home_assistant/packages/cs2_tvled_package.yaml

Add these files:
- docs/ENTITY_CHECKLIST.md
- docs/CS2_CONFIG.md
- cs2/cfg/gamestate_integration_homeassistant.cfg
- home_assistant/manual/scripts.yaml
- home_assistant/manual/automations.yaml

## Version
This bundle uses add-on version:
- 0.3.11

## CS2 config
Use:
- cs2/cfg/gamestate_integration_homeassistant.cfg

Change:
- YOUR_HOME_ASSISTANT_IP

Example:
- http://192.168.178.39:3001/

## Home Assistant package
Put:
- home_assistant/packages/cs2_tvled_package.yaml

into:
- /config/packages/cs2_tvled_package.yaml

Enable packages in configuration.yaml:
```yaml
homeassistant:
  packages: !include_dir_named packages
```

## What users must adapt
1. Replace:
- light.YOUR_TVLED_ENTITY

with the real light entity.

2. In Home Assistant -> Developer Tools -> States search for:
- cs2_gsi_bridge

Verify the bridge entity IDs. If they differ from the package, search/replace them globally.
