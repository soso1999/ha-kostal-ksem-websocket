"""Six phase sensors from local push measurements."""

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import UnitOfElectricCurrent, UnitOfPower
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

SENSORS = tuple(
    SensorEntityDescription(
        key=f"{kind}_l{phase}",
        translation_key=f"{kind}_l{phase}",
        native_unit_of_measurement=unit,
        device_class=device_class,
        state_class=SensorStateClass.MEASUREMENT,
    )
    for kind, unit, device_class in (
        ("current", UnitOfElectricCurrent.AMPERE, SensorDeviceClass.CURRENT),
        ("power", UnitOfPower.WATT, SensorDeviceClass.POWER),
    )
    for phase in (1, 2, 3)
)


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities(
        KsemSensor(entry.runtime_data, entry, description) for description in SENSORS
    )


class KsemSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator, entry, description):
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="KOSTAL Smart Energy Meter",
            manufacturer="KOSTAL",
            model="KSEM",
            configuration_url=f"http://{entry.data['host']}",
        )

    @property
    def native_value(self):
        return self.coordinator.data.get(self.entity_description.key)

    @property
    def available(self):
        return super().available and self.native_value is not None
