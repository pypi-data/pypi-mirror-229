from curl_cffi import requests
import json
import os
import uuid


class Claude:


    def __init__(self, cookie) -> None:
        self.cookies=cookie
        self.organisation_uuid=self.get_organisation_uuid()
        self.conversation_uuid=''
        self.get_conversation_uuid()
        



    def get_organisation_uuid(self):
        uuid=''

        url = 'https://claude.ai/api/organizations'

        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'Content-Type': 'application/json',
            'Cookie': f'{self.cookies}',
            'Referer': 'https://claude.ai/chat/3327f77b-fc2f-4ff3-bf28-2f5ca7e4e84c',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            uuid=data[0]['uuid']

            # Process the response data and analyze the chatbot's API behavior
            # Extract relevant information from the data and observe any patterns
        else:
            # Handle the case when the request is not successful
            print('Request failed with status code:', response.status_code)
            print('Please check the cookies you have entered.')
            print('If they are correct then Claude might be down')
        
        return uuid
    

    def get_random_uuid(self) -> str:

        random_uuid=uuid.uuid4()
        new_uuid=str(random_uuid)
        return new_uuid
    
    def get_conversation_uuid(self):

        url = f'https://claude.ai/api/organizations/{self.organisation_uuid}/chat_conversations'

        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'Content-Type': 'application/json',
            'Cookie': f'{self.cookies}',
            'Referer': 'https://claude.ai/chat/3327f77b-fc2f-4ff3-bf28-2f5ca7e4e84c',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            conversation_history = response.json()
            if(conversation_history==[]):
                print('No old conversations, creating a new one')
                self.create_new_conversation()
                
            else:
                print('Found old conversations, using the most recent one')
                most_receent_conversation=conversation_history[-1]
                self.conversation_uuid=most_receent_conversation['uuid']
                
                
            

            # Process the response data and analyze the chatbot's API behavior
            # Extract relevant information from the data and observe any patterns
        else:
            # Handle the case when the request is not successful
            print('Request failed with status code:', response.status_code)
            print('Please check the cookies you have entered.')
            print('If they are correct then Claude might be down')
        
        return

        

    
    def create_new_conversation(self) -> None:

        url = f"https://claude.ai/api/organizations/{self.organisation_uuid}/chat_conversations"
        conversation_uuid = self.get_random_uuid()

        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'Content-Type': 'application/json',
            'Cookie': f'{self.cookies}',
            'Referer': 'https://claude.ai/chat/3327f77b-fc2f-4ff3-bf28-2f5ca7e4e84c',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
        }

        payload= json.dumps({"uuid": conversation_uuid, "name": ""})

        response = requests.post(url,data=payload, headers=headers)

        if response.status_code == 201:
            data=response.json()

            self.conversation_uuid= data['uuid']
            print('New Conversation Created')
            

            
        
        else:
            print('Request failed with status code:', response.status_code)
            print('Unable to create a new conversation please try again')

        
    
    def get_answer(self,prompt):

        url='https://claude.ai/api/append_message'

        payload=json.dumps({'attachments': [],
                    'completion': { 'incremental': 'true',
                    'model': "claude-2",
                    'prompt': f'{prompt}',
                    'timezone': "Asia/Singapore"},
                    "organization_uuid": f"{self.organization_id}",
                    "conversation_uuid": f"{self.conversation_uuid}",
                    'text': f'{prompt}'})
        
        headers = {
            'User-Agent':
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
            'Accept': 'text/event-stream, text/event-stream',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://claude.ai/chats',
            'Content-Type': 'application/json',
            'Origin': 'https://claude.ai',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Cookie': 'sessionKey=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; intercom-device-id-lupk8zyo=71294eb1-7ab5-45df-aa7b-85d8ece68d74; cf_clearance=_W9h42KkrReUzQOh6spIM4mmvaYlTcMULpQIl1svR3g-1693815950-0-1-8d575e66.d65072bc.da560186-0.2.1693815950; intercom-session-lupk8zyo=NkY0dUlZZEQ5RXFwQXdjeTBlRXpUT2hxQjd4MlFUMXQyQ01Md20zRFU3bWVDSERld0RVWXNsdUUrMW9iL2UyZy0tVURtcXUyZ2ZyekxJOFZKK0tXUDBvUT09--4699b8e0b18b26528dcfe21bd0843f1f54a29979; __cf_bm=yRFrxT3qpv1Ee69Mzjo_K_6ExPT2oPfs_udQUcABmZ0-1693824466-0-AV3qnUmiSFyKJGiwxSjMlSmmXH3w5t+6kT+L7LZuZ9B+O6e/YyIjA0h91aBcuaf2Iek4J8Q9IOaXcyG1K1SDgc0=',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'TE': 'trailers'
        }

        response = requests.post(url, headers=headers, data=payload)

        lines = response.text.split('\n')

        # Extract completion values from lines starting with 'data:'
        completions = ''
        for line in lines:
            if line.startswith('data:'):
                json_str = line.replace('data:', '').strip()
                json_obj = json.loads(json_str)
                completion = json_obj.get('completion')
                if completion is not None:
                    completions+=completion

        # Print the extracted completion values
        # print(completions)
        return completions


    








    





    

    






            



