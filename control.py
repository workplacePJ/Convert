from PostalCodeToLocation.postal_code_to_location import convert_postal_code_to_location
from typing import Any
import aiohttp
import asyncio

async def control(requested_values: list[dict[str, str]]) -> list[dict[str, Any]]:

    async with aiohttp.ClientSession() as session:
        tasks: list = []
        for requested_value in requested_values:
            if "postal_code" in requested_value:
                value: str = requested_value.get('postal_code')
                tasks.append(convert_postal_code_to_location(session, value))
            """
            elif "address" in requested_value:
                value: str = requested_value.get('address')
                tasks.append(convert_location_to_postal_code(session, "address", value))

            elif "landmark" in requested_value:
                value: str = requested_value.get('landmark')
                tasks.append(convert_location_to_postal_code(session, "landmark", value))
            """
        results = await asyncio.gather(*tasks)

    return results
    print(result) 

asyncio.run([{ "postal_code" : "1140034" },{ "postal_code" : "115-0052" }])
