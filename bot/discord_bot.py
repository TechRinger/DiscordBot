import os
import discord
from bot.xsoar.xsoar import XSOARClient
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Modal, TextInput
from time import sleep
import openai
import asyncio
import os

DISCORD_BOT_TOKEN = os.getenv ('DISCORD_BOT_TOKEN')
DISCORD_GUILD = os.getenv ('DISCORD_GUILD')
SOAR_URL = os.getenv('SOAR_URL')
SOAR_API_KEY = os.getenv('SOAR_API_KEY') 
openai.api_key = os.getenv('OPENAI_API_KEY')
SOAR_TYPE = os.getenv('SOAR_TYPE').lower()

xsoar_client = XSOARClient(url=SOAR_URL, api_key=SOAR_API_KEY, bot_type='Discord')


class ModalEmail(Modal, title="Enter email",):
    answer = TextInput(label="Enter email", style=discord.TextStyle.short, required=True)
    user = ''
    incident_type = ''
    inc_id = ''
    async def on_submit(self, interaction):
        print(f'Email is {self.answer}, Discord username is {self.user}, Incident Type is {self.incident_type}')
        self.inc_id = xsoar_client.create_incident(email=self.answer, user=self.user, 
                                                    incident_type=self.incident_type)
        if self.incident_type == "Palo Alto Networks - On Site Spare Replacement Process" or self.incident_type == "Vulnerability Lab Setup":
            embeded_message = discord.Embed(title=f"Hi {self.user}", url=f'{SOAR_URL}/#/incident/{self.inc_id}', description=f"Your incident ID is {self.inc_id}.\n Please check your email for details.", color=0x00ff00)
        else:
            embeded_message = discord.Embed(title=f"Hi {self.user}", url=f'{SOAR_URL}/#/incident/{self.inc_id}', description=f"Your incident ID is {self.inc_id}.", color=0x00ff00)
        await interaction.response.send_message(embed=embeded_message)

class ModalIOC(Modal, title="Create Malicious IOC Entry",):
    answer = TextInput(label="Enter Malicious IOC", style=discord.TextStyle.short, required=True)
    user = ''
    inc_id = ''
    severity = 3
    async def on_submit(self, interaction):
        print(f'IOC is {self.answer}, Discord username is {self.user} with a severity of {self.severity}')
        self.inc_id = xsoar_client.create_ioc(user=self.user, indicator=str(self.answer), severity=self.severity)
        print(self.inc_id)
        if self.inc_id != 'None':
            embeded_message = discord.Embed(title=f"Hi {self.user}", url=f'{SOAR_URL}/#/indicator/{self.inc_id}', description=f"Your IOC was created successfully.", color=0x00ff00)
            await interaction.response.send_message(embed=embeded_message)
        else:
            embeded_message = discord.Embed(title=f"Hi {self.user}", description=f"Your IOC failed to be created.", color=0x00ff00)
            await interaction.response.send_message(embed=embeded_message)

class DropdownView(View):
    @discord.ui.select(min_values=1, max_values=1, options= [
            discord.SelectOption(label='Vulnerability Lab Setup', description='Create your own Vul-Lab instance'),
            discord.SelectOption(label='Palo Alto Networks - On Site Spare Replacement Process', 
                                 description='Get step by step instructions on how to replace your firewall'),
            discord.SelectOption(label='Create Malicious IOC Entry', description='Create a malicious IOC entry'),
            discord.SelectOption(label='Select a CVE', description='Spin up a container to deomonstrate a CVE'),
            discord.SelectOption(label='Hacking Challenge', description='Spin up a vulnerable container for a challenge'),
        ])
    async def select_callback(self, interaction, select):
        if select.values[0] == 'Vul-Lab':
            select.disabled = True
            m = ModalEmail()
            m.user = str(interaction.user)
            m.incident_type = 'Vulnerability Lab Setup'
            await interaction.response.send_modal(m)
        elif select.values[0] == 'Palo Alto Networks - On Site Spare Replacement Process':
            select.disabled = True
            m = ModalEmail()
            m.user = str(interaction.user)
            m.incident_type = select.values[0]
            await interaction.response.send_modal(m)
        elif select.values[0] == 'Create Malicious IOC Entry':
            select.disabled = True
            m = ModalIOC()
            m.user = str(interaction.user)
            m.severity = 3
            await interaction.response.send_modal(m)
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
    client.remove_command('help')

    @client.listen()
    async def on_ready():
        print(f'{client.user} is now running!')
        try:
            synced = await client.tree.sync()
            print(f'Synced {len(synced)} command(s)')
        except Exception as e:
            print(e)

    @client.tree.command(name="create_ioc", description="Create Malicious IOC Entry")
    async def vullab(interaction: discord.Interaction):
            m = ModalIOC()
            m.user = str(interaction.user)
            m.severity = 3
            await interaction.response.send_modal(m)

    @client.tree.command(name="vul-lab", description="Create your own Vul-Lab Instance")
    async def vullab(interaction: discord.Interaction):
            m = ModalEmail()
            m.user = str(interaction.user)
            m.incident_type = 'Vulnerability Lab Setup'
            m.message = 'Create your own Vul-Lab instance'
            await interaction.response.send_modal(m)

    @client.tree.command(name="oss", description="Palo Alto Networks - On Site Spare Replacement Process")
    async def oss(interaction: discord.Interaction,):
            m = ModalEmail()
            m.user = str(interaction.user)
            m.incident_type = 'Palo Alto Networks - On Site Spare Replacement Process'
            await interaction.response.send_modal(m)

    @client.tree.command(name="threat_intel", description="Get Threat Intel")
    @app_commands.describe(message='Threat Intel')  
    async def prompt(interaction: discord.Interaction, message:str):
        try:
            await interaction.response.defer()
            response = openai.ChatCompletion.create(model='gpt-3.5-turbo', messages=[
                {'role': 'system', 'content': 'you are a helpful assistant'},
                {'role': 'user', 'content': f'Provide any information on the cyber threat {message}.  ' +
                 'Use the website https://unit42.paloaltonetworks.com whenever possible and return relient links' }]
            )
            print(response)
            embed = discord.Embed(title='Response', url='', description=f'{response["choices"][0]["message"]["content"]}', color=discord.Color.blue())
            await asyncio.sleep(4)
            await interaction.followup.send(f'{interaction.user.mention}: {message}', embed=embed)
        except Exception as e:
            print(e)
            await interaction.followup.send("There seems to be an issue with ChatGPT, please contact discord admins", ephemeral=True)
            
    @client.tree.command(name="chatgpt", description="Ask ChatGPT")
    @app_commands.describe(message='Ask ChatGPT')
    async def prompt(interaction: discord.Interaction, message:str):
        try:
            await interaction.response.defer()
            response = openai.ChatCompletion.create(model='gpt-3.5-turbo', messages=[
                {'role': 'system', 'content': 'you are a helpful assistant'},
                {'role': 'user', 'content': message}]
            )
            print(response)
            embed = discord.Embed(title='Response', url='', description=f'{response["choices"][0]["message"]["content"]}', color=0x206694)
            await asyncio.sleep(4)
            await interaction.followup.send(f'{interaction.user.mention}: {message}', embed=embed)
        except Exception as e:
            print(e)
            await interaction.followup.send("There seems to be an issue with ChatGPT, please contact discord admins", ephemeral=True)

    @client.listen()
    async def on_message(message):
        if message.author == client.user or message.author.bot == True:
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

        

    client.run(DISCORD_BOT_TOKEN)
