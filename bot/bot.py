import os
import discord
from discord.ext import commands
from discord.ui import View, Modal, TextInput
from dotenv import load_dotenv
import requests
import json


load_dotenv()
TOKEN = os.getenv ('DISCORD_BOT_TOKEN')
GUILD = os.getenv ('DISCORD_GUILD')
XSOAR_URL = os.getenv('XSOAR_URL')
XSOAR_TOKEN = os.getenv('XSOAR_BOT_TOKEN')

def xsoar_create_incident(email: str) -> str:
    body = {'CustomFields': {'emailsender': f'{email}'},
            'name': f'Discord Bot Incident for {email}',
            'playbookId': '9969b7b3-ed19-4d7f-8de2-a165b153f557',
            'type': 'Vulnerability Lab Setup',
            'severity': 1,
            'createInvestigation': True
            }
    headers = {'content-type': 'application/json',
               'accept': 'application/json',
               'Authorization': XSOAR_TOKEN}

    r = requests.post(url=f'{XSOAR_URL}/incident', headers=headers, json=body, verify=False)
    # TODO - sleep and query incident ID for fields
    return r.json()['id']

class modaltest(Modal, title="Enter email"):
    answer = TextInput(label="Enter email", style=discord.TextStyle.short, required=True)
    
    async def on_submit(self, interaction):
        print(self.answer)
        incident_id = xsoar_create_incident(self.answer)
        await interaction.response.send_message(f'{self.answer} - {incident_id} ')

class DropdownView(View):
    @discord.ui.select(min_values=1, max_values=1, options= [
            discord.SelectOption(label='Vul-Lab', description='Create your own Vul-Lab instance'),
            discord.SelectOption(label='Select a CVE', description='Spin up a container to deomonstrate a CVE'),
            discord.SelectOption(label='Hacking Challenge', description='Spin up a vulnerable container for a challenge'),
        ])
    async def select_callback(self, interaction, select):
        if select.values[0] == 'Vul-Lab':
            select.disabled = True
            await interaction.response.send_modal(modaltest())
            # TODO how to disable select and use a modal??
            # await interaction.followup.edit_message(view=self)
        else:
            select.disabled = True
            await interaction.response.edit_message(view=self)
            await interaction.followup.send(f'{select.values[0]} is coming soon')

async def send_message(message, user_message, is_private):
    try:

        view = DropdownView()

        context = message.author if is_private else message.channel
        if user_message.lower() in ["!menu", "!help", "menu", "help"]:
            await context.send(view=view)
        elif user_message.lower() in ["hello","hi"]:
            await context.send("Hey there!")
        else:
            # TODO send to chatgpt
            await context.send("I didn't understand what you wrote. Try typing '!help'")


    except Exception as e:
        print(e)


def run_discord_bot():
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print(f'{client.user} is now running!')

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return
        elif str(message.channel.type) != 'private' and str(message.channel) != 'vul-lab':
            return
        else:

            username = str(message.author)
            user_message = str(message.content)
            channel = str(message.channel)

            print(f'{username} said: "{user_message}" ({channel})')

            if user_message[0] == '?':
                user_message = user_message[1:]
                await send_message(message, user_message, is_private=True)
            else:
                await send_message(message, user_message, is_private=False)
        

    client.run(TOKEN)
