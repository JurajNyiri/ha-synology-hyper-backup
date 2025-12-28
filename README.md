# Synology Hyper Backup

This integration extends the official [Synology DSM integration](https://www.home-assistant.io/integrations/synology_dsm/) in Home Assistant to provide sensors for Hyper Backup.

All entities are grouped under the same device as your existing Synology DSM integration, keeping everything organized.

## Installation

Copy contents of custom_components/synology_hyper_backup/ to custom_components/synology_hyper_backup/ in your Home Assistant config folder.

## Installation using HACS

Add this repository as custom repository.

HACS is a community store for Home Assistant. You can install [HACS](https://github.com/custom-components/hacs) and then install Synology Hyper Backup from the HACS store.

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
