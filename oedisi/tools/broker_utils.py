import helics as h
from pydantic import BaseModel


class TimeData(BaseModel):
    "Time data for a federate"
    name: str
    granted_time: float
    send_time: float


def pprint_time_data(time_data):
    "A table would be better somehow, but which should be the columns"
    print(
        f"""
    Name         : {time_data.name}
    Granted Time : {time_data.granted_time}
    Send Time    : {time_data.send_time}
    """
    )


def parse_time_data(response):
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
    # Use global time debugging?
    return parse_time_data(broker.query("broker", "global_time"))
