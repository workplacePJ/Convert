import PostalCodeToLocation
import postal_code_to_location
from typing import Any
import aiohttp
import asyncio

async def control(requested_values: list[dict[str, str]]) -> list[dict[str, Any]]:

    async with aiohttp.ClientSession() as session:
        tasks: list = []
        for requested_value in requested_values:
            if "postal_code" in requested_value:
                value: str = requested_value.get('postal_code')
                tasks.append(postal_code_to_location.convert_postal_code_to_location(session, value))
            """
            elif "address" in requested_value:
                value: str = requested_value.get('address')
                tasks.append(convert_location_to_postal_code(session, "address", value))

            elif "landmark" in requested_value:
                value: str = requested_value.get('landmark')
                tasks.append(convert_location_to_postal_code(session, "landmark", value))
            """
        results = await asyncio.gather(*tasks)

        print(results)

#if __name__ == "__main__":
    #await main([{"postal_code" : "1150052"}, {"postal_code" : "1140034"}, {"postal_code" : "981-2114"}])
await control([{"postal_code" : "1008111"}, {"postal_code" : "1140052"}, {"postal_code" : "1140034"}, {"postal_code" : "981-2114"}])
#await control([{"address" : "東京都北区上十条2-25"}])
