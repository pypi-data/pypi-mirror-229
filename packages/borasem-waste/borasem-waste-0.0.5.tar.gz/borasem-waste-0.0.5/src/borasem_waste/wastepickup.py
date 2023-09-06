from . import auth


class WastePickup:
    """Class that represents a Waste pickup in the Borås Energi och Miljö API."""

    def __init__(self, raw_data: dict, auth: auth.Auth):
        """Initialize a waste pickup instance."""
        self.raw_data = raw_data
        self.auth = auth

    # Note: each property name maps the name in the returned data

    @property
    def container_id(self) -> str:
        """Return the ID (Kärl X) of the container."""
        return self.raw_data["WasteType"]

    @property
    def next_waste_pickup(self) -> str:
        """Return the next pickup of the Waste container."""
        return self.raw_data["NextWastePickup"]

    @property
    def waste_pickups_per_year(self) -> int:
        """Return the number of pickups per year."""
        return self.raw_data["WastePickupsPerYear"]

    @property
    def waste_pickup_frequency(self) -> str:
        """Return the frequency of the pickups."""
        return self.raw_data["WastePickupFrequency"]

    @property
    def container_type(self) -> int:
        """Return the type of the containers."""
        return self.raw_data["Designation"]

    @property
    def is_active(self) -> bool:
        """Return the if the container delivery is active."""
        return self.raw_data["IsActive"]
