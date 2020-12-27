import datetime

from dataclasses import dataclass


@dataclass
class Trade:
    time: int
    size: float
    price: float

    def __repr__(self):
        local_time = datetime.datetime.fromtimestamp(self.time).strftime("%H:%M:%S")
        return f"{local_time} {round(self.size, 2):<7} {round(self.price, 2)}"
