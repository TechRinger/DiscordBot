# Methods to interact with XSOAR, independant of bot type.
import requests
import re

# Define the regular expressions for each type of input
ip_regex = re.compile(r'\b(?:(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])(?:\[\.\]|\.)){3}(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\b')
cidr_regex = re.compile(r'\b(?:(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])(?:\[\.\]|\.)){3}(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])(\/([0-9]|[1-2][0-9]|3[0-2]))\b')
email_regex = re.compile(r'^[\w\.-]+@[\w\.-]+\.\w+$')
url_regex = re.compile(r'^(http|https|ftp|hxxp|hxxps)://[\w\.-]+\.\w+$')
domain_regex = re.compile(r'^[\w\.-]+\.\w+$')


# Create the dictionary with the compiled regular expressions as values
input_dict = {
    'IP': ip_regex,
    'CIDR': cidr_regex,
    'Email': email_regex,
    'URL': url_regex,
    'Domain': domain_regex
}

# Function to check if the input matches any of the regular expressions
def verify_input(input_str):
    for key, value in input_dict.items():
        if value.match(input_str):
            return key
    return None


# Example usage:
input_str = 'www.google.com'
result = verify_input(input_str)
if result:
    print(f'The input "{input_str}" is a {result}.')
else:
    print(f'The input "{input_str}" is not valid.')

class XSOARClient:
    
    def __init__(self, url:str, api_key:str, bot_type:str):
        self.url = url
        self.bot_type = bot_type
        #self.incident_type = ''
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            'Authorization': api_key
                       }
    
    def create_incident(self, email:str = '', user:str = '', severity:int = 1, incident_type:str = '') -> str:
        if incident_type == "Vulnerability Lab Setup":
            body = {'CustomFields': {
                'emailsender': f'{email}', 
                'emailsubject': f'Vulnerability Lab instance Info for {email}',
                'campaignemailsubject': f'Vulnerability Lab instance Info for {email}',
                'externalsource': f'{self.bot_type}',
                'sourceusername': f'{user}'
                },
            'name': f'{self.bot_type} Bot Incident for {user}',
            'type': f'{incident_type}',
            'severity': severity,
            'createInvestigation': True
            }

            # TODO - query to see if there's already an INC first
            # TODO - SSL cert
        elif incident_type == "Palo Alto Networks - On Site Spare Replacement Process":
            body = {'CustomFields': {
                'emailsender': f'{email}', 
                'emailsubject': f'{incident_type} from XSOAR',
                'campaignemailsubject': f'OSS Procedures for {email}',
                'externalsource': f'{self.bot_type}',
                'sourceusername': f'{user}'
                },
            'name': f'{self.bot_type} Bot created {incident_type} for {user}',
            'type': f'{incident_type}',
            'severity': severity,
            'createInvestigation': True
            }
        else:
            body = {'CustomFields': {
                'emailsender': f'{email}', 
                'emailsubject': f'{incident_type} from XSOAR',
                'campaignemailsubject': f'{incident_type} from XSOAR',
                'externalsource': f'{self.bot_type}',
                'sourceusername': f'{user}'
                },
            'name': f'{self.bot_type} Bot created {incident_type} for {user}',
            'type': f'{incident_type}',
            'severity': severity,
            'createInvestigation': True
            }
        r = requests.post(url=f'{self.url}/incident', headers=self.headers, json=body, verify=False)
        return r.json()['id']       

    def xsoar_query_inc(self, inc_id):
        return_data = {'id': inc_id}

        inc_query = requests.post(url=f'{self.url}/investigation/{inc_id}', headers=self.headers, verify=False)
        j_data = inc_query.json()
        if 'httpsserverport' in j_data.keys():
            return_data['HTTPS Server Port'] = j_data['httpsserverport']
        if 'randomhostname' in inc_query.json().keys():
            return_data['Random Hostname'] = j_data['randomhostname']
        if 'ssltunnelserverport' in inc_query.json().keys():
            return_data['SSL Tunnel Server Port'] = j_data['ssltunnelserverport']
        if 'tcpserverport' in inc_query.json().keys():
            return_data['TCP Server Port'] = j_data['tcpserverport']
        return return_data
    
    def create_ioc_incident(self, user:str = '', severity:int = 1, incident_type:str = '', indicator:str = '', verdict:str = 'Malicious') -> str:
        body = {'CustomFields': {
            'externalsource': f'{self.bot_type}',
            'sourceusername': f'{user}',
            'unknownindicators': f'{indicator}'
            },
        'name': f'{self.bot_type} Bot created IOC: {indicator} for {user}',
        'type': f'{incident_type}',
        'severity': severity,
        'verdict': f'{verdict}',
        'sourceInstance': f'{self.bot_type}',
        'instance': f'{self.bot_type}',
        'createInvestigation': True
        }
        r = requests.post(url=f'{self.url}/incident', headers=self.headers, json=body, verify=False)
        return r.json()['id']
          
    def create_ioc(self, indicator, user:str = '', severity:int = 1, ) -> str:
        indicator_type = verify_input(indicator)

        if indicator_type:
            #body = {
            # "indicator": {
            #     "CustomFields": {
            #         "tags": [
            #             "DiscordBot"
            #         ],
            #         "Username": "CelticChaos#5944"
            #     },
            #     "value": "asdf.fdadsf.com",
            #     "indicator_type": "Domain",
            #     "score": 3,
            #     "comments": [
            #         {
            #             "content": "test comment"
            #         }
            #     ]
            # }
            # }
            body2 = {
            "indicator": {
                "CustomFields": {
                    "tags": [
                        "DiscordBot"
                    ],
                    "Username": f"{user}"
                },
                "value": f"{indicator}",
                "indicator_type": f"{indicator_type}",
                "score": 3,
                "comments": [
                    {
                        "content": "test comment"
                    }
                ]
            }
            }
            body =  { 
              'indicator': {
                'CustomFields': {
                    'tags': [
                        "DiscorBot"
                    ],
                    'Username': f'{user}'
                },
                'value': f'{indicator}',
                'indicator_type': f'{indicator_type}',
                'score': 3,
                'comments': [
                    {
                        'content': f'Created by DiscordBot for {user}'
                    }
                ]
                }
            }
            print(body)
            print(self.url)
            r = requests.post(url=f'{self.url}/indicator/create', headers=self.headers, json=body, verify=False)
            if r.status_code == 200 and r.json()['id'] != '':
                return r.json()['id']
            else:
                print(f'Error {r.status_code}')
        else:
                print(f'The input "{indicator}" is not valid.')
           