"""Utilities for HELICS broker time data management."""

from pydantic import BaseModel


class TimeData(BaseModel):
    """Time data for a federate."""

    name: str
    granted_time: float
    send_time: float


def pprint_time_data(time_data):
    """Pretty print time data for a federate."""
    print(
        f"""
    Name         : {time_data.name}
    Granted Time : {time_data.granted_time}
    Send Time    : {time_data.send_time}
    """
    )


def parse_time_data(response):
    """Parse broker response into list of TimeData objects."""
    time_data = []
    for core in response["cores"]:
        for fed in core["federates"]:
            time_data.append(
                TimeData(
                    name=fed["attributes"]["name"],
                    granted_time=fed["granted_time"],
                    send_time=fed["send_time"],
                )
            )

    return time_data


def get_time_data(broker):
    """Query broker for global time data and parse into TimeData objects."""
    # Use global time debugging?
    return parse_time_data(broker.query("broker", "global_time"))
