"""Platform for sensor integration with Ezetrol Touch."""
import logging
import json
from datetime import timedelta
import aiohttp
import async_timeout
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.const import UnitOfTemperature
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, CONF_IP_ADDRESS, CONF_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up the sensor platform from a config entry."""
    _LOGGER.debug("Setting up Ezetrol Touch sensor platform with IP: %s", entry.data[CONF_IP_ADDRESS])
    ip_address = entry.data[CONF_IP_ADDRESS]
    scan_interval_seconds = entry.data[CONF_SCAN_INTERVAL]
    scan_interval = timedelta(seconds=scan_interval_seconds)
    _LOGGER.debug("Using scan interval: %s seconds", scan_interval_seconds)
    coordinator = EzetrolTouchDataUpdateCoordinator(hass, ip_address, scan_interval)

    # Fetch initial data to ensure the endpoint is reachable
    _LOGGER.debug("Fetching initial data for Ezetrol Touch")
    try:
        await coordinator.async_config_entry_first_refresh()
        _LOGGER.debug("Initial data fetch successful")
    except UpdateFailed as err:
        _LOGGER.error("Failed to fetch initial data for Ezetrol Touch: %s", err)
        return False
    except Exception as err:
        _LOGGER.error("Unexpected error during initial data fetch: %s", err)
        return False

    # Create sensors
    _LOGGER.debug("Creating Ezetrol Touch sensors")
    sensors = [
        EzetrolTouchTemperatureSensor(coordinator),
        EzetrolTouchChlorineSensor(coordinator),
        EzetrolTouchPhSensor(coordinator),
    ]

    async_add_entities(sensors)
    _LOGGER.info("Ezetrol Touch sensors added successfully")
    return True

class EzetrolTouchDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the Ezetrol device."""

    def __init__(self, hass: HomeAssistant, ip_address: str, scan_interval: timedelta):
        """Initialize the coordinator."""
        self.ip_address = ip_address
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=scan_interval,
        )
        self.data = {}

    async def _async_update_data(self):
        """Fetch data from the Ezetrol device."""
        _LOGGER.debug("Starting data fetch from Ezetrol Touch at %s", self.ip_address)
        try:
            url = f"http://{self.ip_address}/ajax_data.json"
            _LOGGER.debug("Requesting data from URL: %s", url)
            async with async_timeout.timeout(10):
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers={'Accept': 'application/json'}) as response:
                        _LOGGER.debug("Received response with status: %s", response.status)
                        _LOGGER.debug("Response headers: %s", dict(response.headers))
                        if response.status != 200:
                            raise UpdateFailed(f"Error fetching data: {response.status}")
                        # Fetch the response as text since Content-Type is text/plain
                        text_data = await response.text(encoding='utf-8-sig')
                        _LOGGER.debug("Received text data (after UTF-8-SIG decoding): %s", text_data)
                        # Manually parse the text as JSON
                        json_data = json.loads(text_data)
                        _LOGGER.debug("Parsed JSON data: %s", json_data)

            d2 = json_data.get("d2")
            if not d2:
                raise UpdateFailed("d2 field not found in JSON response")

            parts = d2.split(';')
            data = {
                "chlorine": "Not found",
                "ph": "Not found",
                "temperature": "Not found"
            }

            for i in range(len(parts)):
                if parts[i] == "2000" and i + 2 < len(parts):
                    data["chlorine"] = parts[i + 1]
                    i += 13
                elif parts[i] == "2172" and i + 2 < len(parts):
                    data["ph"] = parts[i + 1]
                    i += 13
                elif parts[i] == "2688" and i + 2 < len(parts):
                    data["temperature"] = parts[i + 1]
                    i += 13

            _LOGGER.debug("Parsed data: %s", data)
            return data
        except json.JSONDecodeError as err:
            _LOGGER.error("Failed to parse response as JSON: %s", err)
            raise UpdateFailed(f"Failed to parse response as JSON: {err}")
        except Exception as err:
            _LOGGER.error("Error fetching data from Ezetrol Touch: %s", err)
            raise UpdateFailed(f"Error communicating with Ezetrol device: {err}")

class EzetrolTouchTemperatureSensor(SensorEntity):
    """Representation of an Ezetrol Touch Temperature sensor."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__()
        self.coordinator = coordinator
        self._attr_unique_id = "ezetrol_touch_temperature"
        self._attr_name = "Ezetrol Touch Temperature"
        self._attr_device_class = SensorDeviceClass.TEMPERATURE
        self._attr_unit_of_measurement = UnitOfTemperature.CELSIUS
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, "ezetrol_touch_device")},
            name="Ezetrol Touch Device",
            manufacturer="Wallace & Tiernan",
            model="Evoqua"
        )
        _LOGGER.debug("Initialized temperature sensor")

    @property
    def state(self):
        """Return the state of the sensor."""
        state = self.coordinator.data.get("temperature")
        _LOGGER.debug("Temperature sensor state: %s", state)
        return state

    @property
    def available(self):
        """Return True if entity is available."""
        available = self.coordinator.last_update_success
        _LOGGER.debug("Temperature sensor available: %s", available)


        return available

    async def async_update(self):
        """Update the sensor."""
        _LOGGER.debug("Updating temperature sensor")
        await self.coordinator.async_request_refresh()

class EzetrolTouchChlorineSensor(SensorEntity):
    """Representation of an Ezetrol Touch Chlorine sensor."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__()
        self.coordinator = coordinator
        self._attr_unique_id = "ezetrol_touch_chlorine"
        self._attr_name = "Ezetrol Touch Chlorine"
        self._attr_unit_of_measurement = "mg/l"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, "ezetrol_touch_device")},
            name="Ezetrol Touch Device",
            manufacturer="Wallace & Tiernan",
            model="Evoqua"
        )
        _LOGGER.debug("Initialized chlorine sensor")

    @property
    def state(self):
        """Return the state of the sensor."""
        state = self.coordinator.data.get("chlorine")
        _LOGGER.debug("Chlorine sensor state: %s", state)
        return state

    @property
    def available(self):
        """Return True if entity is available."""
        available = self.coordinator.last_update_success
        _LOGGER.debug("Chlorine sensor available: %s", available)
        return available

    async def async_update(self):
        """Update the sensor."""
        _LOGGER.debug("Updating chlorine sensor")
        await self.coordinator.async_request_refresh()

class EzetrolTouchPhSensor(SensorEntity):
    """Representation of an Ezetrol Touch pH sensor."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__()
        self.coordinator = coordinator
        self._attr_unique_id = "ezetrol_touch_ph"
        self._attr_name = "Ezetrol Touch pH"
        self._attr_unit_of_measurement = "pH"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, "ezetrol_touch_device")},
            name="Ezetrol Touch Device",
            manufacturer="Wallace & Tiernan",
            model="Evoqua"
        )
        _LOGGER.debug("Initialized pH sensor")

    @property
    def state(self):
        """Return the state of the sensor."""
        state = self.coordinator.data.get("ph")
        _LOGGER.debug("pH sensor state: %s", state)
        return state

    @property
    def available(self):
        """Return True if entity is available."""
        available = self.coordinator.last_update_success
        _LOGGER.debug("pH sensor available: %s", available)
        return available

    async def async_update(self):
        """Update the sensor."""
        _LOGGER.debug("Updating pH sensor")
        await self.coordinator.async_request_refresh()