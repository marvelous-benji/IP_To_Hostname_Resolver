'''
I made use one the free APIs(which was: https: http://ipwhois.app)
from rapid API which provided reasonable amount of informations
concerning the server the users connected to. A result of the response
is written to the response.json file.
Response with the statement 'IP address not allocated....' means those
IP address are reserved or are multicast ip addresses and not used as
public IP for servers
'''

import json
from loguru import logger


import pandas as pd
import requests


FILE_PATH = "IP.csv"


class IPResolver:
    '''
    Contains all the utility functions
    needed to perform reverse lookup
    on ip addresses
    '''

    IP_RESOLVER_BASE_URL = "http://ipwhois.app/json"
    HEADER = {'Content-Type':'application/json'}


    def __init__(self,file_path=FILE_PATH):
        self.__file_path = file_path
        self._ip_container = set()
        self._response = dict()
        self.transform_csv_to_set()


    def transform_csv_to_set(self):
        '''
        function that reads a csv file
        and transforms the ip address
        column to a set. The  set data
        structure is used here to avoid
        duplication of ip addresses
        '''
        data_frame = pd.read_csv(
            self.__file_path, usecols=["Source", "Destination"], skiprows=[1, 2])
        logger.info('started transformation from csv to set')
        for source, destination in zip(data_frame['Source'], data_frame['Destination']):
            if source.startswith(('192.168','172.16')) is False:
                self._ip_container.add(source)
            if destination.startswith(('192.168','172.16')) is False:
                self._ip_container.add(destination)
            else:
                continue
        logger.info('Finished moving ip address to set')
        logger.info(f'Found {len(self._ip_container)} unique public ips')

    def execute_request(self):
        '''
        This functions Calls all other
        neccessary functions to generate
        a finall result
        '''
        logger.info('Started compiling resolved ips')
        for ip in self._ip_container:
            resp = self.resolve_ip_by_api(ip)
            if resp is None:
                continue
            elif resp['success'] is False:
                self._response[ip] = 'IP address is not allocated to any server but reserved'
            else:
                self._response[ip] = {
                    'orgnization_name':resp['org'],
                    'isp':resp['isp'],
                    'country':resp['country'],
                    'region':resp['region'],
                    'city':resp['city'],
                    'long':resp['longitude'],
                    'lat':resp['latitude'],
                }
        logger.info('Finished compiling resolved ips')
        self.write_ip_info_to_file()

    def resolve_ip_by_api(self, ip):
        '''
        This function interacts with
        https://ipwhois.io API to perform 
        reverse ip lookup
        '''
        
        url = f"{self.IP_RESOLVER_BASE_URL}/{ip}"
        try:
            # Concurency would be more performant for large numbers of IP but here we had only 49 unique IPs
            response = requests.get(url, headers=self.HEADER).json() 
            return response
        except Exception as e:
            logger.error('The error: ',e,'occured when resolving ip: ',ip)
            return None

        
    def write_ip_info_to_file(self):
        '''
        This function writes the reversed
        ip result to a json file
        '''
        logger.info('Started writing to file')
        with open('response.json', 'w') as f:
            f.write(json.dumps(self._response))
        logger.info('Finished writing to file')




instance = IPResolver(FILE_PATH)
instance.execute_request()