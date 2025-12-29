# Synology Hyper Backup

This integration extends the official [Synology DSM integration](https://www.home-assistant.io/integrations/synology_dsm/) in Home Assistant to provide sensors for Hyper Backup.

All entities are grouped under the same device as your existing Synology DSM integration, keeping everything organized.

## Installation

Copy contents of custom_components/synology_hyper_backup/ to custom_components/synology_hyper_backup/ in your Home Assistant config folder.

## Installation using HACS

Add this repository as custom repository.

HACS is a community store for Home Assistant. You can install [HACS](https://github.com/custom-components/hacs) and then install Synology Hyper Backup from the HACS store.

## Card Example

<img width="793" height="198" alt="Screenshot 2025-12-29 at 02 50 15" src="https://github.com/user-attachments/assets/60853f13-4851-44f7-bfc2-5e27016ec8a2" />

```
title: Hyper Backup
path: hyper-backup
icon: mdi:backup-restore
type: custom:layout-card
layout_type: custom:grid-layout
layout:
  grid-template-columns: repeat(auto-fit, minmax(360px, 1fr))
  grid-auto-rows: min-content
  grid-gap: 16px
cards:
  - type: vertical-stack
    cards:
      - type: custom:mushroom-template-card
        primary: "Main: Bratislava"
        entity: sensor.hyper_backup_REPLACE_ME_status_progress_progress
        secondary: >-
          {% set live =
          states('sensor.hyper_backup_REPLACE_ME_status_progress_result')
          %} {% set last =
          states('sensor.hyper_backup_REPLACE_ME_last_result_last_bkp_result')
          %} {% set stage =
          states('sensor.hyper_backup_REPLACE_ME_status_progress_stage')
          %} {% set progress =
          states('sensor.hyper_backup_REPLACE_ME_status_progress_progress')
          %}

          {# progress comes as string; convert safely #} {% set p = progress |
          float(0) %}

          {# Consider "in progress" if live says running OR we have a progress
          number OR a stage #} {% set in_progress = (live == 'running') or (p >
          0) or (stage not in ['unknown','unavailable','none','None','']) %}

          {% if in_progress %}
            Running{{ "· " + stage if stage not in ['unknown','unavailable','none','None',''] else '' }}: {{ p | round(0) }}%
          {% elif last in ['backingup','preparing','starting'] %}
            Starting backup…
          {% else %}
            Last result: {{ last }}
          {% endif %}State: {{
          states('sensor.hyper_backup_REPLACE_ME_status_state') }} ·
          Status: {{
          states('sensor.hyper_backup_REPLACE_ME_status_status') }}
        icon: >-
          {% set st =
          states('sensor.hyper_backup_REPLACE_ME_status_state') %} {%
          set ss =
          states('sensor.hyper_backup_REPLACE_ME_status_status') %} {%
          set live =
          states('sensor.hyper_backup_REPLACE_ME_status_progress_result')
          %} {% set last =
          states('sensor.hyper_backup_REPLACE_ME_last_result_last_bkp_result')
          %} {% set stage =
          states('sensor.hyper_backup_REPLACE_ME_status_progress_stage')
          %} {% set prog_raw =
          states('sensor.hyper_backup_REPLACE_ME_status_progress_progress')
          %} {% set p = prog_raw | float(0) %}

          {% set stage_ok = stage not in
          ['unknown','unavailable','none','None',''] %} {% set prog_ok =
          prog_raw not in ['unknown','unavailable','none','None',''] %} {% set
          in_progress = (live == 'running') or (prog_ok and p > 0) or stage_ok
          %}

          {% if in_progress %}
            mdi:sync
          {% elif ss == 'waiting' %}
            mdi:clock-outline
          {% elif last in ['backingup','preparing','starting'] %}
            mdi:progress-clock
          {% elif last in ['done','success','ok'] %}
            mdi:check-circle
          {% elif last in ['error','failed'] %}
            mdi:alert-circle
          {% else %}
            mdi:backup-restore
          {% endif %}
        icon_color: >-
          {% set st =
          states('sensor.hyper_backup_REPLACE_ME_status_state') %} {%
          set ss =
          states('sensor.hyper_backup_REPLACE_ME_status_status') %} {%
          set live =
          states('sensor.hyper_backup_REPLACE_ME_status_progress_result')
          %} {% set last =
          states('sensor.hyper_backup_REPLACE_ME_last_result_last_bkp_result')
          %} {% set stage =
          states('sensor.hyper_backup_REPLACE_ME_status_progress_stage')
          %} {% set prog_raw =
          states('sensor.hyper_backup_REPLACE_ME_status_progress_progress')
          %} {% set p = prog_raw | float(0) %}

          {% set stage_ok = stage not in
          ['unknown','unavailable','none','None',''] %} {% set prog_ok =
          prog_raw not in ['unknown','unavailable','none','None',''] %} {% set
          in_progress = (live == 'running') or (prog_ok and p > 0) or stage_ok
          %}

          {% if in_progress %}
            blue
          {% elif ss == 'waiting' %}
            grey
          {% elif last in ['backingup','preparing','starting'] %}
            amber
          {% elif last in ['done','success','ok'] %}
            green
          {% elif last in ['error','failed'] %}
            red
          {% else %}
            grey
          {% endif %}
        multiline_secondary: true
        tap_action:
          action: more-info
      - type: grid
        columns: 2
        square: false
        cards:
          - type: custom:mushroom-entity-card
            entity: >-
              sensor.hyper_backup_REPLACE_ME_last_result_last_bkp_success_time
            name: Last Sync
            icon: mdi:clock-check-outline
          - type: custom:mushroom-entity-card
            entity: sensor.hyper_backup_REPLACE_ME_last_result_next_bkp_time
            name: Next Sync
            icon: mdi:clock-outline
      - type: custom:mushroom-template-card
        primary: Last Integrity Check
        secondary: >-
          {% set e =
          'sensor.hyper_backup_REPLACE_ME_integrity_check_time' %} {% if
          has_value(e) %}
            {{ states(e) }}
          {% else %}
            Integrity check not completed.
          {% endif %}
        icon: >-
          {% set e =
          'sensor.hyper_backup_REPLACE_ME_integrity_check_time' %} {% if
          has_value(e) %}
            mdi:shield-check-outline
          {% else %}
            mdi:alert-circle-outline
          {% endif %}
        icon_color: >-
          {% set e =
          'sensor.hyper_backup_REPLACE_ME_integrity_check_time' %} {% if
          has_value(e) %}
            blue
          {% else %}
            red
          {% endif %}
        multiline_secondary: false
```

## Security Notice

**Important:** This integration reuses the credentials from your existing Synology DSM integration to authenticate with your NAS against the DSM API. It only accesses the specific NAS device that you configure with this integration. If you are not comfortable with this credential sharing approach, please do not use this integration.

## Prerequisites

- A Synology NAS device properly configured and accessible
- The official [Synology DSM integration](https://www.home-assistant.io/integrations/synology_dsm/) already set up and working in Home Assistant
- Scheduled tasks configured in your Synology DSM Task Scheduler

## Limitations & Disclaimers

Integration code is partially based on integration https://github.com/bbckr/ha-synology-tasks (at 2025-12-28) which achieves a similar use case - synology tasks.

It is modified to instead get information about Hyper Backup and use library synology_api instead of direct API requests. 
It is also very early version I put together within a few hours just to get the sensors in, breaking changes are to be expected.
