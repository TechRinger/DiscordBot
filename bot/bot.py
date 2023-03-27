import os
import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Modal, TextInput
from dotenv import load_dotenv
import requests
from time import sleep
import openai
import asyncio

# TODO - check into switching from requests to demisto.client

load_dotenv()
TOKEN = os.getenv ('DISCORD_BOT_TOKEN')
GUILD = os.getenv ('DISCORD_GUILD')
XSOAR_URL = os.getenv('XSOAR_URL')
XSOAR_TOKEN = os.getenv('XSOAR_BOT_TOKEN')
XSOAR_PLAYBOOK = os.getenv('XSOAR_PLAYBOOK')
openai.api_key = os.getenv('OPENAI_API_TOKEN')

XSOAR_HEADERS = {'content-type': 'application/json',
            'accept': 'application/json',
            'Authorization': XSOAR_TOKEN}

def xsoar_create_incident(email: str, user:str = '') -> str:
    body = {'CustomFields': {
                'emailsender': f'{email}', 
                'emailsubject': f'Vulnerability Lab for {email}',
                'campaignemailsubject': f'Vulnerability Lab for {email}',
                'externalsource': 'Discord',
                'sourceusername': user
                },
            'name': f'Discord Bot Incident for {email}',
            'playbookId': '{XSOAR_PLAYBOOK}',
            'type': 'Vulnerability Lab Setup',
            'severity': 1,
            'createInvestigation': True
            }

    # TODO - query to see if there's already an INC first
    # TODO - SSL cert
    print(body)
    r = requests.post(url=f'{XSOAR_URL}/incident', headers=XSOAR_HEADERS, json=body, verify=False)
    return r.json()['id']
    

def xsoar_query_inc(inc_id):
    return_data = {'id': inc_id}

    inc_query = requests.post(url=f'{XSOAR_URL}/investigation/{inc_id}', headers=XSOAR_HEADERS, verify=False)
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

class modaltest(Modal, title="Enter email"):
    answer = TextInput(label="Enter email", style=discord.TextStyle.short, required=True)
    user = ''

    async def on_submit(self, interaction):
        print(f'Email is {self.answer}, Discord username is {self.user}')
        inc_id = xsoar_create_incident(self.answer, self.user)
        await interaction.response.send_message(f'{self.answer}, please check your email')

        # TODO - send only to DM and need to wait for the playbook to run
        # sleep(60)
        # inc_data = xsoar_query_inc(inc_id)
        # await interaction.response.send_message(inc_data)

class DropdownView(View):
    @discord.ui.select(min_values=1, max_values=1, options= [
            discord.SelectOption(label='Vul-Lab', description='Create your own Vul-Lab instance'),
            discord.SelectOption(label='Select a CVE', description='Spin up a container to deomonstrate a CVE'),
            discord.SelectOption(label='Hacking Challenge', description='Spin up a vulnerable container for a challenge'),
        ])
    async def select_callback(self, interaction, select):
        if select.values[0] == 'Vul-Lab':
            select.disabled = True
            # The modal needs the discord username passed into it because it doesn't have access
            m = modaltest()
            m.user = str(interaction.user)
            await interaction.response.send_modal(m)
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
    # client = discord.Client(intents=intents)
    client = commands.Bot(command_prefix='!', intents=discord.Intents.all())

    @client.event
    async def on_ready():
        print(f'{client.user} is now running!')
        try:
            synced = await client.tree.sync()
            print(f'Synced {len(synced)} command(s)')
        except Exception as e:
            print(e)

    @client.tree.command(name="hello")
    async def hello(interaction: discord.Interaction):
        await interaction.response.send_message("Hello", ephemeral=True)

    @client.tree.command(name="prompt")
    @app_commands.describe(message='Message for ChatGPT')
    async def prompt(interaction: discord.Interaction, message:str):
        try:
            await interaction.response.defer()
            response = openai.ChatCompletion.create(model='gpt-3.5-turbo', messages=[
                {'role': 'system', 'content': 'you are a helpful assistant'},
                {'role': 'user', 'content': message}]
            )
            print(response)
            embed = discord.Embed(title='Response', url='', description=f'{response["choices"][0]["message"]["content"]}', color=discord.Color.blue())
            await asyncio.sleep(4)
            await interaction.followup.send(f'{interaction.user.mention}: {message}', embed=embed)
        except Exception as e:
            print(e)
            await interaction.followup.send("There seems to be an issue with ChatGPT, please contact discord admins", ephemeral=True)

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
