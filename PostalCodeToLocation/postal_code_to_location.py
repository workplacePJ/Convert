from typing import Any, Pattern
import re
import unicodedata
import aiohttp
import asyncio

async def convert_postal_code_to_location(session, postal_code: str) -> dict[str, Any]:

    """
    Converts a postal code to an address using a postal code API.
    Args:
        session: aiohttp.ClientSession()
        postal_code: The postal code to convert.
    Returns:
        A dictionary containing the location information or error information if an error occurs.
    """

    # generate "result"data
    result: dict[str, Any] = {}

    pattern__judgment_of_postal_code: Pattern[str] = re.compile(r'^(?=.*[0-9]{3}-[0-9]{4})(?=.*[0-9-]{8})(?!.*[0-9-]{9,}).*$|^(?=.*[0-9]{7})(?!.*[0-9-]{8,}).*$')

    if pattern__judgment_of_postal_code.search(postal_code):

        # Hyphenated regular expression
        pattern__hyphenated_postal_code: Pattern[str] = re.compile(r'([0-9]{3}-[0-9]{4})')
        pattern__non_hyphenated_postal_code: Pattern[str] = re.compile(r'([0-9]{7})')

        # Format by checking if the postal code matches the format
        if pattern__hyphenated_postal_code.search(postal_code):
            non_hyphenated_postal_code: str = pattern__hyphenated_postal_code.search(postal_code).group().replace('-','')
        else:
            non_hyphenated_postal_code: str = pattern__non_hyphenated_postal_code.search(postal_code).group()

        # Build URL
        url: str = f"https://workplacepj.github.io/jp-postal-code-api/docs/api/v1/{non_hyphenated_postal_code}.json"

        # API request
        try:
            async with session.get(url) as response:

                response.raise_for_status()
                data: Any = await response.json()

                result['status_code'] = response.status
                result['is_success'] = True
                result['convert_from'] = "postal_code"
                result['requested_value'] = postal_code
                result['results'] = []

                for address in data['addresses']:

                    # data formatting
                    if "address3" in address['ja'] and address['ja']['address3']:
                        address['ja']['address3'] = unicodedata.normalize('NFKC', address['ja']['address3'])
                        if "address3" in address['kana']:
                            address['kana']['address3'] = address['ja']['address3']

                    # complement "kana"data
                    if (not "prefecture" in address['kana'] or ("prefecture" in address['kana'] and not address['kana']['prefecture'])) and (not "address1" in address['kana'] or ("address1" in address['kana'] and not address['kana']['address1'])) and (not "address2" in address['kana'] or ("address2" in address['kana'] and not address['kana']['address2'])):

                        # Build URL
                        complement_url: str = f"https://postcode.teraren.com/postcodes.json?s={address['ja']['prefecture']}{address['ja']['address1']}{address['ja']['address2']}"

                        # API request
                        try:
                            async with session.get(complement_url) as response:

                                response.raise_for_status()
                                data_kana: Any = await response.json()

                                if "prefecture_kana" in data_kana[0] and data_kana[0]['prefecture_kana']:
                                    address['kana']['prefecture'] = data_kana[0]['prefecture_kana']
                                if "city_kana" in data_kana[0] and data_kana[0]['city_kana']:
                                    address['kana']['address1'] = data_kana[0]['city_kana']
                                if "suburb_kana" in data_kana[0] and data_kana[0]['suburb_kana']:
                                    address['kana']['address2'] = data_kana[0]['suburb_kana']

                        # error handling
                        except aiohttp.ClientError as err:
                            pass
                        except Exception as err:
                            pass

                    # generate "result object"data
                    result_object: dict[str, Any] = {}

                    # Assign value to "result object"data
                    if "postalCode" in data and data['postalCode']:
                        result_object['postal_code'] = data['postalCode']
                    if "prefectureCode" in address and address['prefectureCode']:
                        result_object['prefecture_code'] = address['prefectureCode']
                    result_object['ja'] = {}
                    result_object['ja']['full_address'] = ""
                    if "prefecture" in address['ja'] and address['ja']['prefecture']:
                        result_object['ja']['prefecture'] = address['ja']['prefecture']
                        result_object['ja']['full_address'] += address['ja']['prefecture']
                    if "address1" in address['ja'] and address['ja']['address1']:
                        result_object['ja']['city'] = address['ja']['address1']
                        result_object['ja']['full_address'] += address['ja']['address1']
                    if "address2" in address['ja'] and address['ja']['address2']:
                        result_object['ja']['suburb'] = address['ja']['address2']
                        result_object['ja']['full_address'] += address['ja']['address2']
                    if "address3" in address['ja'] and address['ja']['address3']:
                        result_object['ja']['further_divisions'] = address['ja']['address3']
                        result_object['ja']['full_address'] += address['ja']['address3']
                    if "address4" in address['ja'] and address['ja']['address4']:
                        result_object['ja']['enterprise_place'] = address['ja']['address4']
                        result_object['ja']['full_address'] += ' ' + address['ja']['address4']
                    if (not "prefecture" in address['ja'] or ("prefecture" in address['ja'] and not address['ja']['prefecture'])) or (not "address1" in address['ja'] or ("address1" in address['ja'] and not address['ja']['address1'])) or (not "address2" in address['ja'] or ("address2" in address['ja'] and not address['ja']['address2'])):
                        del result_object['ja']['full_address']
                    result_object['kana'] = {}
                    result_object['kana']['full_address'] = ""
                    if "prefecture" in address['kana'] and address['kana']['prefecture']:
                        result_object['kana']['prefecture'] = address['kana']['prefecture']
                        result_object['kana']['full_address'] += address['kana']['prefecture']
                    if "address1" in address['kana'] and address['kana']['address1']:
                        result_object['kana']['city'] = address['kana']['address1']
                        result_object['kana']['full_address'] += address['kana']['address1']
                    if "address2" in address['kana'] and address['kana']['address2']:
                        result_object['kana']['suburb'] = address['kana']['address2']
                        result_object['kana']['full_address'] += address['kana']['address2']
                    if "address3" in address['kana'] and address['kana']['address3']:
                        result_object['kana']['further_divisions'] = address['kana']['address3']
                        result_object['kana']['full_address'] += address['kana']['address3']
                    if "address4" in address['kana'] and address['kana']['address4']:
                        result_object['kana']['enterprise_place'] = address['kana']['address4']
                        result_object['kana']['full_address'] += ' ' + address['kana']['address4']
                    if (not "prefecture" in address['kana'] or ("prefecture" in address['kana'] and not address['kana']['prefecture'])) or (not "address1" in address['kana'] or ("address1" in address['kana'] and not address['kana']['address1'])) or (not "address2" in address['kana'] or ("address2" in address['kana'] and not address['kana']['address2'])):
                        del result_object['kana']['full_address']

                    result['results'].append(result_object)

        # error handling\n","
        except aiohttp.ClientError as err:
            result['status_code'] = response.status
            result['is_success'] = False
            result['convert_from'] = "postal_code"
            result['requested_value'] = postal_code
            result['error'] = f"API request error: {response.status} {err.message}"

        except Exception as err:
            result['status_code'] = response.status
            result['is_success'] = False
            result['convert_from'] = "postal_code"
            result['requested_value'] = postal_code
            result['error'] = "Unexpected error: An unexpected error has occurred."

    else:
        result['status_code'] = None
        result['is_success'] = False
        result['convert_from'] = "postal_code"
        result['requested_value'] = postal_code
        result['error'] = "Format error: Incorrectly formatted postal code"

    return result