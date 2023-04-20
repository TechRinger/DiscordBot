from . import discord_bot
import os



if __name__ == '__main__':
    SOAR_TYPE = os.getenv('SOAR_TYPE').lower()
    if SOAR_TYPE == "xsoar":
        discord_bot.run_discord_bot()
    else:
        print(f'{SOAR_TYPE} is not supported at this time.')
        exit()
