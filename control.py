from PostalCodeToLocation.postal_code_to_location import convert_postal_code_to_location
from typing import Any
import aiohttp
import asyncio

async def control(requested_values: list[dict[str, str]], **kwargs) -> list[dict[str, Any]]:

    async with aiohttp.ClientSession() as session:
        tasks: list = []

        if "KEY" in kwargs and kwargs['KEY']:
            API_KEY: str = kwargs['KEY']

        for requested_value in requested_values:
            if "postal_code" in requested_value:
                value: str = requested_value.get('postal_code')
                tasks.append(convert_postal_code_to_location(session, value, KEY = API_KEY))
            """
            elif "address" in requested_value:
                value: str = requested_value.get('address')
                tasks.append(convert_location_to_postal_code(session, "address", value))

            elif "landmark" in requested_value:
                value: str = requested_value.get('landmark')
                tasks.append(convert_location_to_postal_code(session, "landmark", value))
            """
        results = await asyncio.gather(*tasks)

    #return results
    print(results) 

asyncio.run(control([{ "postal_code" : "1008111" }, { "postal_code" : "115-0052" }, { "postal_code" : "1140034" }], KEY = "AIzaSyC7dLXM_6HyFxVvLVPnCLnV2uTdwqgYOKM"))
