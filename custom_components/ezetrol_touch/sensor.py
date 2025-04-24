"""Platform for sensor integration with Ezetrol Touch."""
import logging
import aiohttp
import async_timeout
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.const import UnitOfTemperature
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, CONF_IP_ADDRESS, SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up the sensor platform from a config entry."""
    ip_address = entry.data[CONF_IP_ADDRESS]
    coordinator = EzetrolTouchDataUpdateCoordinator(hass, ip_address)

    # Fetch initial data to ensure the endpoint is reachable
    await coordinator.async_config_entry_first_refresh()

    # Create sensors
    sensors = [
        EzetrolTouchTemperatureSensor(coordinator),
        EzetrolTouchChlorineSensor(coordinator),
        EzetrolTouchPhSensor(coordinator),
    ]

    async_add_entities(sensors)

class EzetrolTouchDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the Ezetrol device."""

    def __init__(self, hass: HomeAssistant, ip_address: str):
        """Initialize the coordinator."""
        self.ip_address = ip_address
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )
        self.data = {}

    async def _async_update_data(self):
        """Fetch data from the Ezetrol device."""
        try:
            url = f"http://{self.ip_address}/ajax_data.json"
            async with async_timeout.timeout(10):
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        if response.status != 200:
                            raise UpdateFailed(f"Error fetching data: {response.status}")
                        json_data = await response.json()

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

            return data
        except Exception as err:
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

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get("temperature")

    @property
    def available(self):
        """Return True if entity is available."""
        return self.coordinator.last_update_success

    async def async_update(self):
        """Update the sensor."""
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

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get("chlorine")

    @property
    def available(self):
        """Return True if entity is available."""
        return self.coordinator.last_update_success

    async def async_update(self):
        """Update the sensor."""
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

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get("ph")

    @property
    def available(self):
        """Return True if entity is available."""
        return self.coordinator.last_update_success

    async def async_update(self):
        """Update the sensor."""
        await self.coordinator.async_request_refresh()