"""The hub  for powerplanner."""
from datetime import datetime

import aiohttp
import pytz

class PowerplannerHub:
    """Hub for powerplanner."""

    manufacturer = "NomKon AB"

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        self.schedules = None
        self.plans = None
        self.updated: datetime
        self.plansChanged = False
        self.changeCallback = None
        self.addSensorCallback  = None
        self.removeSensorCallback = None
        self.sensors: list[any] = []
        self.oldPlans: list[str] = []
        self.newPlans: list[str] = []

    async def __fetch(self, read: bool = False) -> aiohttp.ClientResponse:
        async with aiohttp.ClientSession() as session, session.get(
            "https://www.powerplanner.se/api/scheme/?token=" + self.api_key
        ) as resp:
            if read:
                await resp.read()
            return resp

    async def update(self) -> None:
        """Update all schedules."""
        resp = await self.__fetch(True)
        json = await resp.json()

        self.schedules = json["schedules"]
        self.updated = datetime.now()
        updatedPlans = list(self.schedules)
        self.newPlans = self._getNewPlans(updatedPlans, self.plans)
        self.oldPlans = self._getRemovedPlans(updatedPlans, self.plans)
        self.plansChanged = self.oldPlans is not None or self.newPlans is not None
        self.plans = updatedPlans

        return json

    def addSensor(self, sensor):
        self.sensors.append(sensor)
        self.addSensorCallback([sensor])

    async def removeSensor(self, sensorName: str):
        found = None
        for sensor in self.sensors:
            if sensor.scheduleName == sensorName:
                found = sensor
                break

        if found is None:
            return

        await found.async_remove()
        self.sensors.remove(found)

    def timeToChange(self, name) -> int:
        if name not in self.plans:
            return 0

        currentValue = self._currentValue(name)
        nextValue = self._nextValue(name, not currentValue)

        if nextValue is None:
            return 0

        currentTime = self._currentTime()
        changeTime = self._parseTime(nextValue["startTime"], currentTime.tzinfo)
        delta = changeTime - self._currentTime()

        return delta.seconds

    def is_on(self, name) -> bool:
        if self.schedules is None or name not in self.plans:
            return False

        nowStr = self._currentTimeStr()
        schedule = list(self.schedules[name])

        filetered = list(filter(lambda x: x["enabled"] is True, schedule))
        filetered = list(filter(lambda x: x["startTime"] <= nowStr, filetered))
        filetered = list(filter(lambda x: x["endTime"] > nowStr, filetered))
        return len(filetered) > 0

    async def authenticate(self) -> bool:
        """Test if we can authenticate with the host."""
        resp = await self.__fetch()
        return resp.status == 200

    def _getNewPlans(self, newPlans, oldPlans) -> list[str]:
        return self._getMissing(newPlans, oldPlans)

    def _getRemovedPlans(self, newPlans, oldPlans):
        return self._getMissing(oldPlans, newPlans)

    def _getMissing(self, a, b) -> list[str]:
        result = []

        if a is None:
            return []

        if b is None:
            return a

        for x in a:
            found = False
            for y in b:
                if x == y:
                    found = True

            if found is False:
                result.append(x)

        return result

    def _currentValue(self, name) -> bool:
        nowStr = self._currentTimeStr()
        schedule = list(self.schedules[name])

        filetered = list(filter(lambda x: x["startTime"] <= nowStr, schedule))
        filetered = list(filter(lambda x: x["endTime"] > nowStr, filetered))
        if len(filetered) == 0:
            return False
        return filetered[0]["enabled"]

    def _nextValue(self, name, value: bool):
        nowStr = self._currentTimeStr()
        schedule = list(self.schedules[name])

        filetered = list(filter(lambda x: x["enabled"] == value, schedule))
        filetered = list(filter(lambda x: x["startTime"] > nowStr, filetered))
        if len(filetered) == 0:
            return None
        return filetered[0]

    def _currentTime(self):
        return datetime.now(tz=pytz.timezone("Europe/Stockholm"))

    def _currentTimeStr(self):
        nowStr = self._currentTime().strftime("%Y-%m-%dT%H:%M:%S")
        return nowStr

    def _parseTime(self, string: str, tzInfo):
        time = datetime.strptime(
            string,
            "%Y-%m-%dT%H:%M:%S",
        )

        return datetime(
            time.year,
            time.month,
            time.day,
            time.hour,
            time.minute,
            time.second,
            tzinfo=tzInfo,
        )
