










































async def convert_location_to_postal_code(session, location_type: str, location: str) -> dict[str, Any]:
    """
    Converts a location to an postal code using a geo API.
    Args:
        session: aiohttp.ClientSession()
        location: The location to convert.
    Returns:
        A dictionary containing the postal code information or error information if an error occurs.
    """
    # generate "result"data
    result: dict[str, Any] = {}

    # API request
    try:
        url: Literal = "https://maps.googleapis.com/maps/api/geocode/json"
        API_KEY: Literal = "AIzaSyC7dLXM_6HyFxVvLVPnCLnV2uTdwqgYOKM"
        params: dict[str, str] = { "key" : API_KEY, "language" : "ja", "address" : location}

        async with session.get(url = url, params = params) as response:

            response.raise_for_status()
            data: Any = await response.json()

            # address element of data
            address_components: list[dict[str, str | list]] = data['results'][0]['address_components']

            if "address" in location_type:
                # generate "acquired object"data
                acquired_object: dict[str, str] = {}
                acquired_object['further_divisions'] = {}

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
