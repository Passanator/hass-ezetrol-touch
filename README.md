# Ezetrol Touch Integration for Home Assistant

This integration fetches pool data (chlorine, pH, temperature) from a Wallace & Tiernan Evoqua Ezetrol Touch device and exposes it as sensors in Home Assistant.

## Installation via HACS

To add this integration to HACS, use this link: [Add to HACS](https://my.home-assistant.io/redirect/hacs_repository/?owner=Passanator&repository=hass-ezetrol-touch&category=integration)

Alternatively, you can manually add the repository:

1. Open HACS in Home Assistant.
2. Go to **Integrations** > Click the three dots (⋮) > **Custom repositories**.
3. Add the repository URL: `https://github.com/Passanator/hass-ezetrol-touch`.
4. Set the category to **Integration**.
5. Click **Add**.
6. Search for "Ezetrol Touch" in HACS and install it.
7. Restart Home Assistant.

## Configuration

1. After installing, go to **Settings > Devices & Services** in Home Assistant.
2. Click **Add Integration** and search for "Ezetrol Touch".
3. Enter the IP address of your Ezetrol Touch device (e.g., `192.168.1.235`).
4. Set the scan interval in seconds (default is 300 seconds, or 5 minutes). Do not set below 60 seconds to avoid system instability.
5. Submit the configuration to add the integration.

## Sensors

- `sensor.ezetrol_touch_chlorine`: Chlorine level in mg/l.
- `sensor.ezetrol_touch_ph`: pH level.
- `sensor.ezetrol_touch_temperature`: Temperature in °C.

## Notes

- The integration polls the device at the interval you configure (default is 5 minutes).
- Ensure your Home Assistant instance can access the device on your local network.