import sys
import requests

from xml.etree import cElementTree as ElementTree  # for zillow API

from .pyzillowerrors import ZillowError, ZillowFail, ZillowNoResults
from . import __version__


class ZillowWrapper(object):
    """
    """

    def __init__(self, api_key=None):
        """

        """
        self.api_key = api_key

    def get_deep_search_results(self, address, zipcode):
        """
        GetDeepSearchResults API
        """

        url = 'http://www.zillow.com/webservice/GetDeepSearchResults.htm'
        params = {
            'address': address,
            'citystatezip': zipcode,
            'zws-id': self.api_key
        }
        return self.get_data(url, params)

    def get_updated_property_details(self, zpid):
        """
        GetUpdatedPropertyDetails API
        """
        url = 'http://www.zillow.com/webservice/GetUpdatedPropertyDetails.htm'

        params = {
            'zpid': zpid,
            'zws-id': self.api_key
        }
        return self.get_data(url, params)

    def get_zestimate(self, zpid):
        """
        GetZestimate API
        """
        url = 'http://www.zillow.com/webservice/GetZestimate.htm'

        params = {
            'zpid': zpid,
            'zws-id': self.api_key
        }
        return self.get_data(url, params)

    def get_data(self, url, params):
        """
        """

        try:
            request = requests.get(
                url=url,
                params=params,
                headers={
                    'User-Agent': ''.join([
                        'pyzillow/',
                        __version__,
                        ' (Python)'
                    ])
                })
        except (
            requests.exceptions.ConnectionError,
            requests.exceptions.TooManyRedirects,
                requests.exceptions.Timeout):
            raise ZillowFail

        try:
            request.raise_for_status()
        except requests.exceptions.HTTPError:
            raise ZillowFail

        try:
            response = ElementTree.fromstring(request.text)
        except ElementTree.ParseError:
            print (
                "Zillow response is not a valid XML (%s)" % (
                    params['address']
                )
            )
            raise ZillowFail

        if response.findall('message/code')[0].text is not '0':
            raise ZillowError(int(response.findall('message/code')[0].text))
        else:
            if not response.findall('response'):
                print (
                    "Zillow returned no results for (%s)" % (
                        params['address']
                    )
                )
                raise ZillowNoResults
            return response


class ZillowResults(object):
    """
    """

    attribute_mapping = {}

    def get_attr(self, attr):
        """
        """
        try:
            return self.data.find(self.attribute_mapping[attr]).text
        except AttributeError:
            return None

    def __unicode__(self):
        return self.zillow_id

    if sys.version_info[0] >= 3:  # Python 3
        def __str__(self):
            return self.__unicode__()

    else:  # Python 2
        def __str__(self):
            return self.__unicode__().encode('utf8')

    @property
    def area_unit(self):
        """
        lotSizeSqFt
        """
        return u'SqFt'

    @property
    def last_sold_price_currency(self):
        """
        lastSoldPrice currency
        """
        return self.data.find(
            self.attribute_mapping['last_sold_price']).attrib["currency"]


class GetDeepSearchResults(ZillowResults):
    """
    """
    attribute_mapping = {
        'zillow_id': 'result/zpid',
        'home_type': 'result/useCode',
        'home_detail_link': 'result/links/homedetails',
        'graph_data_link': 'result/links/graphsanddata',
        'map_this_home_link': 'result/links/mapthishome',
        'comparables_link': 'result/links/comparables',
        'latitude': 'result/address/latitude',
        'longitude': 'result/address/longitude',
        'FIPS_county_code': 'result/FIPScounty',
        'tax_year': 'result/taxAssessmentYear',
        'tax_value': 'result/taxAssessment',
        'year_built': 'result/yearBuilt',
        'property_size': 'result/lotSizeSqFt',
        'home_size': 'result/finishedSqFt',
        'bathrooms': 'result/bathrooms',
        'bedrooms': 'result/bedrooms',
        'last_sold_date': 'result/lastSoldDate',
        'last_sold_price': 'result/lastSoldPrice',
        'zestimate_amount': 'result/zestimate/amount',
        'zestimate_last_updated': 'result/zestimate/last-updated',
        'zestimate_value_change': 'result/zestimate/valueChange',
        'zestimate_valuation_range_high':
        'result/zestimate/valuationRange/high',
        'zestimate_valuationRange_low': 'result/zestimate/valuationRange/low',
        'zestimate_percentile': 'result/zestimate/percentile',
        'region_zindex_value': 'result/localRealEstate/region/zindexValue',
        'region_overview_link': 'result/localRealEstate/region/links/overview',
        'region_fsbo_link':
        'result/localRealEstate/region/links/forSaleByOwner',
        'region_for_sale_link': 'result/localRealEstate/region/links/forSale',
    }

    def __init__(self, data, *args, **kwargs):
        """
        Creates instance of GeocoderResult from the provided XML data array
        """
        self.data = data.findall('response/results')[0]
        for attr in self.attribute_mapping.__iter__():
            try:
                self.__setattr__(attr, self.get_attr(attr))
            except AttributeError:
                print ('AttributeError with %s' % attr)


class GetUpdatedPropertyDetails(ZillowResults):
    """
    """
    attribute_mapping = {
        # attributes in common with GetDeepSearchResults
        'zillow_id': 'zpid',
        'home_type': 'editedFacts/useCode',
        'home_detail_link': 'links/homeDetails',
        'graph_data_link': '',
        'map_this_home_link': '',
        'street_address': 'address/street',
        'zipcode': 'address/zipcode',
        'city': 'address/city',
        'state': 'address/state',
        'latitude': 'address/latitude',
        'longitude': 'address/longitude',
        'tax_year': '',
        'tax_value': '',
        'year_built': 'editedFacts/yearBuilt',
        'property_size': 'editedFacts/lotSizeSqFt',
        'home_size': 'editedFacts/finishedSqFt',
        'bathrooms': 'editedFacts/bathrooms',
        'bedrooms': 'editedFacts/bedrooms',
        'last_sold_date': '',
        'last_sold_price': '',
        # new attributes in GetUpdatedPropertyDetails
        'photo_gallery': 'links/photoGallery',
        'home_info': 'links/homeInfo',
        'year_updated': 'editedFacts/yearUpdated',
        'floor_material': 'editedFacts/floorCovering',
        'num_floors': 'editedFacts/numFloors',
        'basement': 'editedFacts/basement',
        'roof': 'editedFacts/roof',
        'view': 'editedFacts/view',
        'parking_type': 'editedFacts/parkingType',
        'heating_sources': 'editedFacts/heatingSources',
        'heating_system': 'editedFacts/heatingSystem',
        'rooms': 'editedFacts/rooms',
        'num_rooms': 'editedFacts/numRooms',
        'appliances': 'editedFacts/appliances',
        'exterior_material': 'editedFacts/exteriorMaterial',
        'architecture': 'editedFacts/architecture',
        'num_units': 'editedFacts/numUnits',
        'neighborhood': 'neighborhood',
        'school_district': 'schoolDistrict',
        'home_description': 'homeDescription',
    }

    def __init__(self, data, *args, **kwargs):
        """
        Creates instance of GeocoderResult from the provided XML data array
        """
        self.data = data.findall('response')[0]
        for attr in self.attribute_mapping.__iter__():
            try:
                self.__setattr__(attr, self.get_attr(attr))
            except AttributeError:
                print ('AttributeError with %s' % attr)


class GetZestimate(ZillowResults):
    """
    """
    attribute_mapping = {
        'zillow_id': 'zpid',
        'home_detail_link': 'links/homedetails',
        'graph_data_link': 'links/graphsanddata',
        'map_this_home_link': 'links/mapthishome',
        'comparables_link': 'links/comparables',
        'street_address': 'address/street',
        'zipcode': 'address/zipcode',
        'city': 'address/city',
        'state': 'address/state',
        'latitude': 'address/latitude',
        'longitude': 'address/longitude',
        'zestimate_amount': 'zestimate/amount',
        'zestimate_last_updated': 'zestimate/last-updated',
        'zestimate_value_change': 'zestimate/valueChange',
        'zestimate_valuation_range_high': 'zestimate/valuationRange/high',
        'zestimate_valuation_range_low': 'zestimate/valuationRange/low',
        'zestimate_percentile': 'zestimate/percentile',
        'region_zindex_value': 'localRealEstate/region/zindexValue',
        'region_overview_link': 'localRealEstate/region/links/overview',
        'region_fsbo_link': 'localRealEstate/region/links/forSaleByOwner',
        'region_for_sale_link': 'localRealEstate/region/links/forSale',
        'zipcode_id': 'regions/zipcode-id',
        'city_id': 'regions/city-id',
        'county_id': 'regions/county-id',
        'state_id': 'regions/state-id',
    }

    def __init__(self, data, *args, **kwargs):
        """
        Creates instance of GeocoderResult from the provided XML data array
        """
        self.data = data.findall('response')[0]
        for attr in self.attribute_mapping.__iter__():
            try:
                self.__setattr__(attr, self.get_attr(attr))
            except AttributeError:
                print ('AttributeError with %s' % attr)

