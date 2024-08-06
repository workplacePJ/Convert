from typing import Any, Pattern, Literal
import re
import unicodedata
import aiohttp
import asyncio

async def convert_location_to_postal_code(session, location_type: Literal["address", "landmark"], location: str, **kwargs) -> dict[str, Any]:
    """
    Converts a location to an postal code using a geo API.
    Args:
        session: aiohttp.ClientSession()
        location_type: Location type
        location: The location to convert.
    Returns:
        A dictionary containing the postal code information or error information if an error occurs.
    API used:
        Google maps Platform
        https://console.cloud.google.com/google/maps-apis/api-list?project=api-project-430803&authuser=2&hl=ja
    """
    
    # generate "result"data
    result: dict[str, Any] = {}

    if location:
        # Build URL
        base_url: str = "https://maps.googleapis.com/maps/api/geocode/json"
        
        # API_KEY
        API_KEY: str = kwargs.get('KEY', '')
    
        # params
        params: dict[str, str] = { "key" : API_KEY, "language" : "ja", "address" : location}

        # API request
        try:
            async with session.get(url = base_url, params = params) as response:
                response.raise_for_status()
                data: Any = await response.json()
                
                # address element of data
                address_components: list[dict[str, Any]] = data['results'][0]['address_components']
                
                if location_type == "address":
                    # generate "acquired object"data
                    acquired_object: dict[str, str] = {}
                elif location_type == "landmark":
                
                


                
                for address_component in address_components:
                    # Assign value to "acquired_object"data
                    if "sublocality_level_3" in address_component['types'] or "sublocality_level_4" in address_component['types'] or "premise" in address_component['types']:
                        if not "further_divisions" in acquired_object:
                            acquired_object['further_divisions'] = {}
                        
                        if "sublocality_level_3" in address_component['types']:
                            acquired_object['further_divisions']['chome'] = re.sub(r'[^0-9０-９]+', '', address_component['long_name'])
                        elif "sublocality_level_4" in address_component['types']:
                        elif "premise" in address_component['types']:
                        
                        
                    elif "postal_code" in address_component['types']:
                        acquired_object['postal_code'] = address_component['long_name'].replace('-','')
                    elif "administrative_area_level_1" in address_component['types']:
                        acquired_object['prefecture'] = address_component['long_name']
                    elif "locality" in address_component['types']:
                        acquired_object['city'] = address_component['long_name']
                    elif "sublocality_level_2" in address_component['types']:
                        acquired_object['suburb'] = address_component['long_name']

                    


                    
                    elif "sublocality_level_3" in address_component['types']:
                        chome: str = unicodedata.normalize('NFKC', address_component['long_name'])
                        acquired_object['further_divisions']['chome'] = re.sub(r'\D', '', chome)
                        
                    elif "sublocality_level_4" in address_component['types']:
                        acquired_object['further_divisions']['banchi'] = unicodedata.normalize('NFKC', address_component['long_name'])
                    
                    elif "premise" in address_component['types']:
                        if address_component['long_name'].isdecimal():
                            acquired_object['further_divisions']['gou'] = unicodedata.normalize('NFKC', address_component['long_name'])
                        else:
                            acquired_object['building_name'] = address_component['long_name']








    
    else:
        result['status_code'] = None
        result['is_success'] = False
        result['convert_from'] = location_type
        result['requested_value'] = location
        result['error'] = "Error: Matching value was not found"
                        






        

async def convert_postal_code_to_location(session, postal_code: str, **kwargs) -> dict[str, Any]:

    """
    Converts a postal code to an address using a postal code API.
    Args:
        session: aiohttp.ClientSession()
        postal_code: The postal code to convert.
    Returns:
        A dictionary containing the location information or error information if an error occurs.
    API used:
        PostcodeJp
        https://console.postcode-jp.com/dashbord
    """

    # generate "result"data
    result: dict[str, Any] = {}

    # postal code formatting
    postal_code = unicodedata.normalize('NFKC', postal_code)
    
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
        base_url: Literal = "https://apis.postcode-jp.com/api/v6"
        url: str = f"{base_url}/postcodes/{non_hyphenated_postal_code}"
        
        # API_KEY
        API_KEY: str = kwargs.get('KEY', '')
        
        # headers
        headers: dict[str, str] = {"Content-Type": "application/json", "apikey": API_KEY}
        
        # API request
        try:
            async with session.get(url = url, headers = headers) as response:
                response.raise_for_status()
                data: Any = await response.json()

                if data:
                    result['status_code'] = response.status
                    result['is_success'] = True
                    result['convert_from'] = "postal_code"
                    result['requested_value'] = postal_code
                    result['results'] = []
                    
                    pattern__further_divisions: Pattern[str] = re.compile(r'([0-9０-９-－]+)$')
                    
                    for item in data:
                        # generate "result object"data
                        result_object: dict[str, Any] = {}
    
                        # Assign value to "result object"data
                        if "postcode" in item:
                            result_object['postal_code'] = item.get('postcode')
                        if "prefCode" in item:
                            result_object['prefecture_code'] = item.get('prefCode')
                        
                        result_object['ja'] = {}
                        if "pref" in item:
                            result_object['ja']['prefecture'] = item.get('pref')
                        if "city" in item:
                            result_object['ja']['city'] = item.get('city')
                        if "town" in item:
                            if pattern__further_divisions.search(item.get('town')):
                                result_object['ja']['suburb'] = item.get('town').replace(pattern__further_divisions.search(item.get('town')).group(), '')
                                result_object['ja']['further_divisions'] = pattern__further_divisions.search(item.get('town')).group()
                            else:
                                result_object['ja']['suburb'] = item.get('town')
                        if "office" in item:
                            result_object['ja']['enterprise_place'] = item.get('office')
                        if "allAddress" in item:
                            result_object['ja']['full_address'] = item.get('allAddress')
    
                        if "fullWidthKana" in item:
                            result_object['kana'] = {}
                            if "pref" in item['fullWidthKana']:
                                result_object['kana']['prefecture'] = item['fullWidthKana'].get('pref')
                            if "city" in item['fullWidthKana']:
                                result_object['kana']['city'] = item['fullWidthKana'].get('city')
                            if "town" in item['fullWidthKana']:
                                if pattern__further_divisions.search(item['fullWidthKana'].get('town')):
                                    result_object['kana']['suburb'] = item['fullWidthKana'].get('town').replace(pattern__further_divisions.search(item['fullWidthKana'].get('town')).group(), '')
                                    result_object['kana']['further_divisions'] = pattern__further_divisions.search(item['fullWidthKana'].get('town')).group()
                                else:
                                    result_object['kana']['suburb'] = item['fullWidthKana'].get('town')
                            if "office" in item['fullWidthKana']:
                                result_object['kana']['enterprise_place'] = item['fullWidthKana'].get('office')
                            if "allAddress" in item['fullWidthKana']:
                                result_object['kana']['full_address'] = item['fullWidthKana'].get('allAddress')
                        
                        if "ja" in result_object:
                            if "further_divisions" in result_object['ja']:
                                if "location" in item:
                                    if "latitude" in item['location'] or "longitude" in item['location']:
                                        result_object['location'] = {}
                                        if "latitude" in item['location']:
                                            result_object['location']['lat'] = item['location'].get('latitude')
                                        if "longitude" in item['location']:
                                            result_object['location']['lng'] = item['location'].get('longitude')
                        
                        result['results'].append(result_object)
                        
                else:
                    result['status_code'] = response.status
                    result['is_success'] = False
                    result['convert_from'] = "postal_code"
                    result['requested_value'] = postal_code
                    result['error'] = "Error: Matching value was not found"
                    
        # error handling","
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
            result['error'] = "Unexpected error: An unexpected error has occurred"

    else:
        result['status_code'] = None
        result['is_success'] = False
        result['convert_from'] = "postal_code"
        result['requested_value'] = postal_code
        result['error'] = "Format error: Incorrectly formatted postal code"

    return result










































            

                for address_component in address_components:

                    # Assign value to "acquired_object object"data
                    if "postal_code" in address_component['types']:
                        acquired_object['postal_code'] = address_component['long_name'].replace('-','')
                    elif "administrative_area_level_1" in address_component['types']:
                        acquired_object['prefecture'] = address_component['long_name']
                    elif "locality" in address_component['types']:
                        acquired_object['city'] = address_component['long_name']
                    elif "sublocality_level_2" in address_component['types']:
                        acquired_object['suburb'] = address_component['long_name']
                    elif "sublocality_level_3" in address_component['types']:
                        chome: str = unicodedata.normalize('NFKC', address_component['long_name'])
                        acquired_object['further_divisions']['chome'] = re.sub(r'\D', '', chome)
                    elif "sublocality_level_4" in address_component['types']:
                        acquired_object['further_divisions']['banchi'] = unicodedata.normalize('NFKC', address_component['long_name'])
                    elif "premise" in address_component['types']:
                        if address_component['long_name'].isdecimal():
                            acquired_object['further_divisions']['gou'] = unicodedata.normalize('NFKC', address_component['long_name'])
                        else:
                            acquired_object['building_name'] = address_component['long_name']

                # Joining "further divisions"data
                if acquired_object['further_divisions']:
                    if "chome" in acquired_object['further_divisions']:
                        acquired_object['further_divisions']['joined_data'] = acquired_object['further_divisions']['chome']
                        if "banchi" in acquired_object['further_divisions']:
                            acquired_object['further_divisions']['joined_data'] += "-" + acquired_object['further_divisions']['banchi']
                            if "gou" in acquired_object['further_divisions']:
                                acquired_object['further_divisions']['joined_data'] += "-" + acquired_object['further_divisions']['gou']

                if acquired_object['prefecture'] in location and acquired_object['city'] in location and acquired_object['suburb'] in location:

                    result['status_code'] = response.status
                    result['is_success'] = True
                    result['convert_from'] = location_type
                    result['requested_value'] = location
                    result['results'] = []

                    # generate "result object"data
                    result_object: dict[str, Any] = {}

                    # Assign value to "result object"data
                    result_object['postal_code'] = acquired_object['postal_code']
                    result_object['prefecture_code'] = None
                    result_object['ja'] = {}
                    result_object['ja']['prefecture'] = acquired_object['prefecture']
                    result_object['ja']['city'] = acquired_object['city']
                    result_object['ja']['suburb'] = acquired_object['suburb']
                    if acquired_object['further_divisions']:
                        result_object['ja']['further_divisions'] = acquired_object['further_divisions']['joined_data']
                    if "building_name" in acquired_object:
                        result_object['ja']['building_name'] = acquired_object['building_name']
                        result_object['ja']['full_address'] = f"{acquired_object['prefecture']}{acquired_object['city']}{acquired_object['suburb']}{acquired_object['further_divisions']['joined_data']} {acquired_object['building_name']}"
                    else:
                        result_object['ja']['full_address'] = f"{acquired_object['prefecture']}{acquired_object['city']}{acquired_object['suburb']}{acquired_object['further_divisions']['joined_data']}"

                    """
                    result_object['kana'] = {}
                    result_object['kana']['prefecture'] = address['kana']['prefecture']
                    result_object['kana']['city'] = address['kana']['address1']
                    result_object['kana']['suburb'] = address['kana']['address2']
                    if address['kana']['address3']:
                        result_object['kana']['further_divisions'] = address['kana']['address3']
                    if address['kana']['address4']:
                        result_object['kana']['enterprise_place'] = address['kana']['address4']
                        result_object['kana']['full_address'] = f"{address['kana']['prefecture']}{address['kana']['address1']}{address['kana']['address2']}{address['kana']['address3']} {address['kana']['address4']}"
                    else:
                        result_object['kana']['full_address'] = f"{address['kana']['prefecture']}{address['kana']['address1']}{address['kana']['address2']}{address['kana']['address3']}{address['kana']['address4']}"
                    result['results'].append(result_object)
                    """








                    result['results'].append(result_object)
                #else:
                    #エラー処理：入力住所と違う場合の処理













            elif "landmark" in location_type:
                # geometry element of data
                geometry: dict[str, Any] = data['results'][0]['geometry']
                acquired_object['geometry'] = {}
                acquired_object['geometry']['lat'] = geometry['location']['lat']
                acquired_object['geometry']['lng'] = geometry['location']['lng']



            #result['results'].append(acquired_object)








        """
        # complement "kana"data
        # Build URL
        complement_url:str = f"https://postcode.teraren.com/postcodes.json?s={acquired_object['prefecture']}{acquired_object['city']}{acquired_object['suburb']}"

        # API request
        try:
            async with session.get(complement_url) as response:
                response.raise_for_status()
                data_kana: Any = await response.json()

                address['kana']['prefecture'] = data_kana[0]['prefecture_kana']
                address['kana']['address1'] = data_kana[0]['city_kana']
                address['kana']['address2'] = data_kana[0]['suburb_kana']

        # error handling
        except aiohttp.ClientError as err:
            result['status_code'] = response.status
            result['is_success'] = False
            result['convert_from'] = f"{location_type}_kana"
            result['requested_value'] = postal_code
            result['error'] = f"API request error: {response.status} {err.message}"

        except Exception as err:
            result['status_code'] = response.status
            result['is_success'] = False
            result['convert_from'] = f"{location_type}_kana"
            result['requested_value'] = postal_code
            result['error'] = "Unexpected error: An unexpected error has occurred."
        """













    except aiohttp.ClientError as err:
        result['status_code'] = response.status
        result['is_success'] = False
        result['convert_from'] = location_type
        result['requested_value'] = location
        result['error'] = f"API request error: {response.status} {err.message}"
    """
    except Exception as err:
        result['status_code'] = response.status
        result['is_success'] = False
        result['convert_from'] = location_type
        result['requested_value'] = location
        result['error'] = "Unexpected error: An unexpected error has occurred."
    """
    return result
