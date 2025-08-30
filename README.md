# Synology Tasks HACS Integration

## Requirements
- Docker or Podman
- pipx
- Poetry
    ```
    pipx install poetry
    ```

## Debugging against Home Assistant Locally

1. Run `docker-compose up`
1. Open http://0.0.0.0:8123 in your browser
1. Setup the first user
1. Install the **Remote Python Debugger** by adding the following to your configuration.yaml:
    ```
    debugpy:
    start: true
    wait: false
    ```
1. Run the **Home Assistant: Attach Remote** launch.json configuration
1. Set your breakpoints
1. Profit
