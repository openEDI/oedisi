"""HELICS federate configuration types for type-safe simulation setup."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field
from oedisi.types.common import BrokerConfig


class HELICSBrokerConfig(BaseModel):
    """HELICS broker connection parameters.

    Parameters
    ----------
    host :
        Broker hostname or IP address.
    port :
        Broker port number.
    key :
        Broker key for authentication.
    auto :
        Whether to automatically configure broker connection.
    initstring :
        Additional initialization string for broker connection.
    """

    model_config = ConfigDict(populate_by_name=True)

    host: str | None = None
    port: int | None = None
    key: str | None = None
    auto: bool | None = None
    initstring: str | None = Field(default=None, alias="initString")

    @classmethod
    def from_rest_config(cls, rest: BrokerConfig) -> HELICSBrokerConfig:
        """Convert REST API BrokerConfig to HELICS native broker config."""
        return cls(host=rest.broker_ip, port=rest.broker_port)


class HELICSFederateConfig(BaseModel):
    """Full HELICS federate configuration.

    This is what federates receive in static_inputs.json under the `federate_config` key.
    Subtype this in your applications for custom configuration.

    Parameters
    ----------
    name :
        Federate name (derived from Component.name).
    core_type :
        HELICS core type (e.g., "zmq", "tcp", "inproc").
    core_name :
        Core name for this federate (derived per-component).
    core_init_string :
        Core initialization string.
    broker :
        Broker connection configuration.

    Examples
    --------
    >>> config = HELICSFederateConfig(
    ...     name="state_estimator",
    ...     core_type="zmq",
    ...     broker=HELICSBrokerConfig(port=23404)
    ... )
    >>> config.to_json()
    '{"name": "state_estimator", "coreType": "zmq", ...}'
    """

    model_config = ConfigDict(populate_by_name=True)

    name: str
    core_type: str | None = Field(default=None, alias="coreType")
    core_name: str | None = Field(default=None, alias="coreName")
    core_init_string: str | None = Field(default=None, alias="coreInitString")
    broker: HELICSBrokerConfig | None = None

    def to_json(self) -> str:
        """Serialize to JSON string using HELICS-style camelCase keys."""
        return self.model_dump_json(by_alias=True, exclude_none=True)

    def to_dict(self) -> dict:
        """Convert to dictionary using HELICS-style camelCase keys."""
        return self.model_dump(by_alias=True, exclude_none=True)

    def apply_to_federate_info(self, info) -> None:
        """Apply configuration to a helics.HelicsFederateInfo object.

        Parameters
        ----------
        info :
            A helics.HelicsFederateInfo object to configure.

        Notes
        -----
        This method requires the helics Python package to be installed.
        It modifies the info object in place.
        """
        if self.core_type is not None:
            info.core_type = self.core_type
        if self.core_name is not None:
            info.core_name = self.core_name
        if self.core_init_string is not None:
            info.core_init_string = self.core_init_string
        if self.broker is not None:
            if self.broker.host is not None:
                info.broker = self.broker.host
            if self.broker.port is not None:
                info.broker_port = self.broker.port
            if self.broker.key is not None:
                info.broker_key = self.broker.key

    @classmethod
    def from_multicontainer(
        cls,
        broker_config: BrokerConfig,
        name: str,
        core_type: str = "zmq",
        **kwargs,
    ) -> HELICSFederateConfig:
        """Create federate config for multicontainer deployments.

        This is a convenience method for components running in Docker/Kubernetes
        that receive BrokerConfig from the broker service's /run endpoint.

        Parameters
        ----------
        broker_config :
            REST API broker configuration from /run endpoint.
        name :
            Federate name (typically from static_inputs.json).
        core_type :
            HELICS core type, defaults to "zmq".
        **kwargs :
            Additional federate config options (core_name, core_init_string, etc).

        Returns
        -------
        HELICSFederateConfig
            Complete federate configuration ready to apply.

        Examples
        --------
        >>> # In component server.py /run endpoint
        >>> with open("static_inputs.json") as f:
        ...     params = json.load(f)
        >>> config = HELICSFederateConfig.from_multicontainer(
        ...     broker_config=broker_config,
        ...     name=params["name"]
        ... )
        >>> fedinfo = h.helicsCreateFederateInfo()
        >>> config.apply_to_federate_info(fedinfo)
        """
        return cls(
            name=name,
            core_type=core_type,
            broker=HELICSBrokerConfig.from_rest_config(broker_config),
            **kwargs,
        )


class SharedFederateConfig(BaseModel):
    """Shared federate settings at the WiringDiagram level.

    This contains settings that are shared across all federates in a simulation.
    Does NOT include name/core_name (those are per-component).

    Parameters
    ----------
    core_type :
        HELICS core type (e.g., "zmq", "tcp", "inproc").
    core_init_string :
        Core initialization string.
    broker :
        Broker connection configuration.

    Examples
    --------
    >>> shared = SharedFederateConfig(
    ...     core_type="zmq",
    ...     broker=HELICSBrokerConfig(port=23404)
    ... )
    >>> config = shared.to_federate_config("my_federate")
    >>> config.name
    'my_federate'
    """

    model_config = ConfigDict(populate_by_name=True)

    core_type: str | None = Field(default=None, alias="coreType")
    core_init_string: str | None = Field(default=None, alias="coreInitString")
    broker: HELICSBrokerConfig | None = None

    def to_federate_config(
        self, name: str, core_name: str | None = None
    ) -> HELICSFederateConfig:
        """Create a full HELICSFederateConfig for a specific component.

        Parameters
        ----------
        name :
            Federate name (typically Component.name).
        core_name :
            Optional core name for this federate.

        Returns
        -------
        HELICSFederateConfig
            Complete federate configuration with per-component values set.
        """
        return HELICSFederateConfig(
            name=name,
            core_name=core_name,
            core_type=self.core_type,
            core_init_string=self.core_init_string,
            broker=self.broker,
        )
