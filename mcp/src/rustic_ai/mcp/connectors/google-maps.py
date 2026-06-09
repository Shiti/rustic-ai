"""
Auto-generated Pydantic models for google-maps's MCP. Supported tools are:
search_places : Call this tool when the user's request is to find places, businesses, addresses, locations, points of interest, or any other Google Maps related search.

**Input Requirements (CRITICAL):**

1.  **`text_query` (string - MANDATORY):** The primary search query. This must clearly define what the user is looking for.

    *   **Examples:** `'restaurants in New York'`, `'coffee shops near Golden Gate Park'`, `'SF MoMA'`, `'1600 Amphitheatre Pkwy, Mountain View, CA, USA'`, `'pets friendly parks in Manhattan, New York'`, `'date night restaurants in Chicago'`, `'accessible public libraries in Los Angeles'`.

    *   **For specific place details:** Include the requested attribute (e.g., `'Google Store Mountain View opening hours'`, `'SF MoMa phone number'`, `'Shoreline Park Mountain View address'`).

2.  **`location_bias` (object - OPTIONAL):** Use this to prioritize results near a specific geographic area.
    *   **Format:** `{"location_bias": {"circle": {"center": {"latitude": [value], "longitude": [value]}, "radius_meters": [value (optional)]}}}`

    *   **Usage:**
        *   **To bias to a 5km radius:** `{"location_bias": {"circle": {"center": {"latitude": 34.052235, "longitude": -118.243683}, "radius_meters": 5000}}}`
        *   **To bias strongly to the center point:** `{"location_bias": {"circle": {"center": {"latitude": 34.052235, "longitude": -118.243683}}}}` (omitting `radius_meters`).

3. **`language_code` (string - OPTIONAL):** The language to show the search results summary in.
    *   **Format:** A two-letter language code (ISO 639-1), optionally followed by an underscore and a two-letter country code (ISO 3166-1 alpha-2), e.g., `en`, `ja`, `en_US`, `zh_CN`, `es_MX`. If the language code is not provided, the results will be in English.

4. **`region_code` (string - OPTIONAL):** The Unicode CLDR region code of the user. This parameter is used to display the place details, like region-specific place name, if available. The parameter canaffect results based on applicable law.
    *   **Format:** A two-letter country code (ISO 3166-1 alpha-2), e.g., `US`, `CA`.

**Instructions for Tool Call:**

*   Location Information (CRITICAL): The search must contain sufficient location information. If the location is ambiguous (e.g., just "pizza places"), *you must* specify it in the `text_query` (e.g., "pizza places in New York") or use the `location_bias` parameter. Include city, state/province, and region/country name if needed for disambiguation.

*   Always provide the most specific and contextually rich `text_query` possible.

*   Only use `location_bias` if coordinates are explicitly provided or if inferring a location from a user's known context is appropriate *and* necessary for better results.

*   The grounded output must be attributed to the source using the information from the `attribution` field when available.

lookup_weather : Retrieves comprehensive weather data including current conditions, hourly, and daily forecasts.

**Specific Data Available:** Temperature (Current, Feels Like, Max/Min, Heat Index), Wind (Speed, Gusts, Direction), Celestial Events (Sunrise/Sunset, Moon Phase), Precipitation (Type, Probability, Quantity/QPF), Atmospheric Conditions (UV Index, Humidity, Cloud Cover, Thunderstorm Probability), and Geocoded Location Address.

**Location & Location Rules (CRITICAL):**

The location for which weather data is requested is specified using the `location` field.
This field is a 'oneof' structure, meaning you MUST provide a value for ONLY ONE
of the three location sub-fields below to ensure an accurate weather data lookup.

1.  Geographic Coordinates (lat_lng)
    *   Use it when you are provided with exact lat/lng coordinates.
    *   Example:
        {"location": {"lat_lng": {"latitude": 34.0522, "longitude": -118.2437}}} // Los Angeles

2.  Place ID (place_id)
    *   An unambiguous string identifier (Google Maps Place ID).
    *   The place_id can be fetched from the search_places tool.
    *   Example:
        {"location": {"place_id": "ChIJLU7jZClu5kcR4PcOOO6p3I0"}} // Eiffel Tower

3.  Address String (address)
    *   A free-form string that requires specificity for geocoding.
    *   City & Region: Always include region/country (e.g., "London, UK", not "London").
    *   Street Address: Provide the full address (e.g., "1600 Pennsylvania Ave NW, Washington, DC").
    *   Postal/Zip Codes: MUST be accompanied by a country name (e.g., "90210, USA", NOT "90210").
    *   Example:
        {"location": {"address": "1600 Pennsylvania Ave NW, Washington, DC"}}

**Usage Modes:**

*   **Current Weather:** Provide `location` only. Do not specify `date` and `hour`.

*   **Hourly Forecast:** Provide `location`, `date`, and `hour` (0-23). Use for specific times (e.g., "at 5 PM") or terms like "next few hours" or "later today". If the user specifies minute, round down to the nearest hour. Hourly forecast beyond 120 hours from now is not supported. Historical hourly weather is supported up to 24 hours in the past.

*   **Daily Forecast:** Provide `location` and `date`. Do not specify `hour`. Use for general day requests (e.g., "weather for tomorrow", "weather on Friday", "weather on 12/25"). If today's date is not in the context, you should clarify it with the user. Daily forecast beyond 10 days including today is not supported. Historical weather is not supported.

**Parameter Constraints:**

*   **Timezones:** All `date` and `hour` inputs must be relative to the **location's local time zone**, not the user's time zone.
*   **Date Format:** Inputs must be separated into `{year, month, day}` integers.
*   **Units:** Defaults to `METRIC`. Set `units_system` to `IMPERIAL` for Fahrenheit/Miles if the user implies US standards or explicitly requests it.

*   The grounded output must be attributed to the source using the information from the `attribution` field when available.

compute_routes : Computes a travel route between a specified origin and destination. **Supported Travel Modes:** DRIVE (default), WALK.

**Input Requirements (CRITICAL):**
Requires both **origin** and **destination**. Each must be provided using one of the following methods, nested within its respective field:

*   **address:** (string, e.g., 'Eiffel Tower, Paris'). Note: The more granular or specific the input address is, the better the results will be.

*   **lat_lng:** (object, {"latitude": number, "longitude": number})

*   **place_id:** (string, e.g., 'ChIJOwE_Id1w5EAR4Q27FkL6T_0') Note: This id can be obtained from the search_places tool.
Any combination of input types is allowed (e.g., origin by address, destination by lat_lng). If either the origin or destination is missing, **you MUST ask the user for clarification** before attempting to call the tool.

**Example Tool Call:**
{"origin":{"address":"Eiffel Tower"},"destination":{"place_id":"ChIJt_5xIthw5EARoJ71mGq7t74"},"travel_mode":"DRIVE"}

*   The grounded output must be attributed to the source using the information from the `attribution` field when available.

resolve_names : Resolves a batch list of specific location queries (landmark names or exact addresses) into canonical Google Maps Place IDs.

**Input Requirements (CRITICAL):**

1.  **`queries` (array of objects - MANDATORY):** A list of location queries to resolve. You may specify up to 20 queries.
    *   **Each query object must have:**
        *   **`text` (string - MANDATORY):** The text query representing a specific place name or address to resolve.
            *   **Examples:** `'Googleplex, Mountain View, CA'`, `'1600 Amphitheatre Pkwy, Mountain View, CA'`, `'Eiffel Tower, Paris'`.

2.  **`location_bias` (object - OPTIONAL):** Use this to prioritize results near a specific geographic area.
    *   **Format:** `{"viewport": {"low": {"latitude": [value], "longitude": [value]}, "high": {"latitude": [value], "longitude": [value]}}}`

3.  **`region_code` (string - OPTIONAL):** The Unicode CLDR region code (two-letter country code, e.g., `US`, `CA`) of the user to bias the results.

**Instructions for Tool Call:**

*   Specificity (CRITICAL): Queries must represent a specific place name or address. General searches like `'restaurants'` or chain names like `'Starbucks'` are not supported.
*   Do NOT call this tool if the downstream tools you plan to invoke already accept raw address or place name strings directly.

**Error Handling (CRITICAL):**

*   This is a batch processing tool. A request might return "mixed results" (e.g. some queries resolve successfully while others fail).
*   The output list of `results` is guaranteed to map 1:1 with the input `queries` indices. A failed query will result in an empty `Result` message (no `entity` is set) at its corresponding index in the `results` list.
*   You **MUST** check the `failed_requests` map field in the response to identify which specific query index failed. The key of `failed_requests` represents the 0-based index of the failed query in the request. Do not assume the entire batch call failed because of a partial failure.

resolve_maps_urls : Resolves a list of Google Maps URLs into canonical Google Maps Place IDs.

**When to call this tool (CRITICAL):**

*   Use this tool when the user provides one or more Google Maps sharing links or URLs (e.g. 'https://maps.app.goo.gl/...', 'https://www.google.com/maps/place/...', or 'https://maps.google.com/...') and you need to extract the underlying canonical Place IDs.
*   You can specify up to 20 URLs to resolve in a single batch request.

**Input Requirements (CRITICAL):**

*   **`urls` (array of strings - MANDATORY):** The list of Google Maps URLs to resolve. Each URL must be a valid, single-place Google Maps URL.

**Error Handling (CRITICAL):**

*   This is a batch processing tool. A request might return "mixed results" (e.g. some URLs resolve successfully while others fail).
*   The output list of `entities` is guaranteed to map 1:1 with the input `urls` indices. A failed URL resolution will result in an empty `Entity` message (no fields are set) at its corresponding index in the `entities` list.
*   You **MUST** check the `failed_requests` map field in the response to identify which specific URL index failed. The key of `failed_requests` represents the 0-based index of the failed URL in the request. Do not assume the entire batch call failed because of a partial failure.


Example BoundMCPAgentConfig (JSON) for this provider:
 {
   "server": {
     "type": "http",
     "url": "https://mapstools.googleapis.com/mcp"
   },
   "tools": [
     {
       "name": "search_places",
       "input_class_name": "rustic_ai.mcp.connectors.google-maps.SearchPlacesInput"
     },
     {
       "name": "lookup_weather",
       "input_class_name": "rustic_ai.mcp.connectors.google-maps.LookupWeatherInput"
     },
     {
       "name": "compute_routes",
       "input_class_name": "rustic_ai.mcp.connectors.google-maps.ComputeRoutesInput"
     },
     {
       "name": "resolve_names",
       "input_class_name": "rustic_ai.mcp.connectors.google-maps.ResolveNamesInput"
     },
     {
       "name": "resolve_maps_urls",
       "input_class_name": "rustic_ai.mcp.connectors.google-maps.ResolveMapsUrlsInput"
     }
   ]
 }

"""  # noqa

from enum import Enum
from typing import Annotated, Any, Optional

from pydantic import BaseModel, Field, RootModel


class UnitsSystem(Enum):
    """
    Optional. The units system to use for the returned weather conditions. If not provided, the returned weather
    conditions will be in the metric system (default = METRIC).
    """

    UNITS_SYSTEM_UNSPECIFIED = "UNITS_SYSTEM_UNSPECIFIED"
    IMPERIAL = "IMPERIAL"
    METRIC = "METRIC"


class TravelMode(Enum):
    """
    Optional. Specifies the mode of transportation.
    """

    ROUTE_TRAVEL_MODE_UNSPECIFIED = "ROUTE_TRAVEL_MODE_UNSPECIFIED"
    DRIVE = "DRIVE"
    WALK = "WALK"


class ResolveMapsUrlsInput(BaseModel):
    """
    Request message for ResolveMapsUrls.
    """

    urls: Annotated[
        list[str],
        Field(
            description=(
                "Required. The Google Maps URLs to be resolved. Each URL should be a valid Google Maps URL, for"
                " example, https://maps.app.goo.gl/..., https://www.google.com/maps/place/..., or"
                " https://maps.google.com/.... Currently, only URLs pointing to a single place are supported. You may"
                " specify up to 20 URLs."
            )
        ),
    ]


class Date(RootModel[Any]):
    root: Any


class Location(RootModel[Any]):
    root: Any


class LocationBias(RootModel[Any]):
    root: Any


class LocationQuery(RootModel[Any]):
    root: Any


class Waypoint(RootModel[Any]):
    root: Any


class SearchPlacesInput(BaseModel):
    """
    Request message for SearchText.
    """

    languageCode: Annotated[
        Optional[str],
        Field(
            description=(
                "Optional. The language to request that the summary is returned in. If the language code is unspecified"
                ' or unrecognized, the summary with a preference for English will be returned. For example, "en" for'
                " English. Current list of supported languages: https://developers.google.com/maps/faq#languagesupport."
            )
        ),
    ] = None
    locationBias: Annotated[
        Optional[LocationBias],
        Field(
            description=(
                "An optional region to bias the search results to. If an explicit location is in `text_query`, it will"
                " be used to bias the search results instead of this field."
            )
        ),
    ] = None
    regionCode: Annotated[
        Optional[str],
        Field(
            description=(
                "Optional. The Unicode country/region code (CLDR) of the location where the request is coming from."
                " This parameter is used to display the place details, like region-specific place name, if available."
                ' The parameter can affect results based on applicable law. For example, "US" for United States. For'
                " more information, see"
                " https://www.unicode.org/cldr/charts/latest/supplemental/territory_language_information.html. Note"
                " that 3-digit region codes are not currently supported."
            )
        ),
    ] = None
    textQuery: Annotated[str, Field(description="Required. The text query.")]


class LookupWeatherInput(BaseModel):
    """
    Request for the LookupWeather method - represents the weather conditions at the requested location.
    """

    date: Annotated[
        Optional[Date],
        Field(
            description=(
                "Optional. The date of the required weather information. Note: This date is relative to the local"
                " timezone of the location specified in the location field. The date must be between 24 hours in the"
                " past and the next 10 days."
            )
        ),
    ] = None
    hour: Annotated[
        Optional[int],
        Field(
            description=(
                "Optional. The hour of the requested weather information, in 24-hour format (0-23). This value is"
                " relative to the local timezone of the location specified in the location field. Hourly forecast"
                " beyond 120 hours from now is not supported. Historical hourly weather is supported up to 24 hours in"
                " the past."
            )
        ),
    ] = None
    location: Annotated[Location, Field(description="Required. The location to get the weather conditions for.")]
    unitsSystem: Annotated[
        Optional[UnitsSystem],
        Field(
            description=(
                "Optional. The units system to use for the returned weather conditions. If not provided, the returned"
                " weather conditions will be in the metric system (default = METRIC)."
            )
        ),
    ] = None


class ComputeRoutesInput(BaseModel):
    """
    ComputeRoutesRequest.
    """

    destination: Annotated[Waypoint, Field(description="Required. Destination waypoint.")]
    origin: Annotated[Waypoint, Field(description="Required. Origin waypoint.")]
    travelMode: Annotated[
        Optional[TravelMode], Field(description="Optional. Specifies the mode of transportation.")
    ] = None


class ResolveNamesInput(BaseModel):
    """
    Request message for ResolveNames.
    """

    locationBias: Annotated[
        Optional[LocationBias],
        Field(
            description=(
                "Optional. An optional region to bias the resolution results. If specified, the resolution results will"
                " be biased towards the entities that are closer to this region. Including `location_bias` or"
                " `region_code` often provides better results by narrowing the search space. If both `location_bias`"
                " and `region_code` are specified, `location_bias` takes precedence over `region_code`."
            )
        ),
    ] = None
    queries: Annotated[
        list[LocationQuery],
        Field(description="Required. A list of location queries to be resolved. You may specify up to 20 queries."),
    ]
    regionCode: Annotated[
        Optional[str],
        Field(
            description=(
                "Optional. An optional region code to bias the resolution results. If specified, the resolution results"
                " will be biased towards the entities that are in or near the specified region. This should be a CLDR"
                ' region code. For example, "US" or "CA". Including `location_bias` or `region_code` often provides'
                " better results by narrowing the search space. If both `location_bias` and `region_code` are"
                " specified, `location_bias` takes precedence over `region_code`."
            )
        ),
    ] = None
