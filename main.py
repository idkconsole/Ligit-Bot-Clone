import os
import json
import time, asyncio
import discord,requests
from jishaku import Jishaku
from datetime import datetime
from discord.ext import commands
from dhooks import Webhook, Embed

client = commands.Bot(command_prefix = ";", help_command = None, intents = discord.Intents.all())

with open("config.json", "r") as f:
    var = json.load(f)

with open("db.json", "r") as f:
    a = json.load(f)
  
token = var["bot-token"]
vanity = var["vanity"]
category_id = var["role-access-category"]
slot_access_category = var["slot-access-category"]
slot_category_id = var["slots-cate"]
blacklisted = a["blacklisted"]
utoken = var["user-token"]
hook = var["slot-webhook"]
huk = var["role-webhook"]
hoo = var["bl-webhook"]
premium_users_role = var["premium-users-role"]
newbiesrole = var["role-id"]

@client.event
async def on_ready():
    os.system("clear || cls")
    tree = await client.tree.sync()

@client.event
async def on_message(message):
    if message.author.bot:
        return
    if "@everyone" in message.content and not message.author.guild_permissions.administrator:
        channel = message.channel
        user = message.author
        await channel.set_permissions(user, send_messages=False, read_message_history=False, mention_everyone=False)
        await channel.send(f"Revoked Slot | Reason: Everyone ping")
    await client.process_commands(message)

def sendLogs(url: str, embed: bool, content: str):
    webhook = Webhook(url = url)
    if embed == True:
        embed = Embed(title = "New Log", description = content)
        webhook.send(embed = embed)
    else:
        webhook.send(content = content)

@client.tree.command()
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"{round(client.latency * 100)}ms")

@client.command()
async def ping(ctx):
  await ctx.reply(f"{round(client.latency * 100)}ms")

@client.tree.command(description="Add an User to the Blacklisted Database.", name="add_blacklist")
async def add_user(ctx: discord.Interaction, *, user: discord.User):
    with open("config.json", "r") as f:
        config = json.load(f)
    owners = config["owners"]
    if int(ctx.user.id) in owners:
        with open("db.json", "r") as ff:
            bl = json.load(ff)
        if int(user.id) not in bl["blacklisted"]:
            bl["blacklisted"].append(int(user.id))
            with open("db.json", "w") as ff:
                json.dump(bl, ff, indent=4)
            await ctx.response.send_message(f"{user} has been added to the blacklisted list!")
            sendLogs(hoo, True, f"{user.mention} has been added to the blacklisted list.\n**Added by: {ctx.user.mention}**")
        else:
            await ctx.response.send_message(f"{user} is already in the blacklisted list.")
    else:
        await ctx.response.send_message("unauthorized")

@client.tree.command(description="Remove an User From the Blacklisted Database.", name="remove_blacklist")
async def remove_user(ctx: discord.Interaction, *, user: discord.User):
    with open("config.json", "r") as f:
        config = json.load(f)
    owners = config["owners"]
    if int(ctx.user.id) in owners:
        with open("db.json", "r") as ff:
            bl = json.load(ff)
        if int(user.id) in bl["blacklisted"]:
            bl["blacklisted"].remove(int(user.id))
            with open("db.json", "w") as ff:
                json.dump(bl, ff, indent=4)
            await ctx.response.send_message(f"{user} has been removed from the blacklisted list!")
            sendLogs(hoo, True, f"{user.mention} has been removed from the blacklisted list.\n**Removed by: {ctx.user.mention}**")
        else:
            await ctx.response.send_message(f"{user} is not in the blacklisted list.")
    else:
        await ctx.response.send_message("unauthorized")

@client.tree.command(description = "set webhook for slot logs.", name = "set_slothook")
async def sethook(ctx: discord.Interaction, *, url: str):
    with open("config.json", "r") as f:
        config = json.load(f)
    owners = config["owners"]
    if int(ctx.user.id) in owners:
        config["slot-webhook"] = url
        with open("config.json", "w") as f:
            json.dump(config, f, indent=4)
        await ctx.response.send_message(f"Webhook URL for slot logs has been set")
    else:
        await ctx.response.send_message("unauthorized")

@client.tree.command(description = "set webhook for role logs.", name = "set_rolehook")
async def sethook(ctx: discord.Interaction, *, url: str):
    with open("config.json", "r") as f:
        config = json.load(f)
    owners = config["owners"]
    if int(ctx.user.id) in owners:
        config["role-webhook"] = url
        with open("config.json", "w") as f:
            json.dump(config, f, indent=4)
        await ctx.response.send_message(f"Webhook URL for role logs has been set")
    else:
        await ctx.response.send_message("unauthorized")

@client.tree.command(description = "set webhook for blacklist logs.", name = "set_blhook")
async def sethook(ctx: discord.Interaction, *, url: str):
    with open("config.json", "r") as f:
        config = json.load(f)
    owners = config["owners"]
    if int(ctx.user.id) in owners:
        config["bl-webhook"] = url
        with open("config.json", "w") as f:
            json.dump(config, f, indent=4)
        await ctx.response.send_message(f"Webhook URL for blacklist logs has been set")
    else:
        await ctx.response.send_message("unauthorized")

@client.tree.command()
async def set_newbierole(ctx: discord.Interaction, *, role: discord.Role):
    with open("config.json", "r") as f:
        config = json.load(f)
    owners = config["owners"]
    if int(ctx.user.id) in owners:
        config["role-id"] = role.id
        with open("config.json", "w") as f:
            json.dump(config, f, indent=4)
        await ctx.response.send_message(f"Newbie role has been set to {role.mention}")
    else:
        await ctx.response.send_message("unauthorized")

@client.tree.command()
async def set_premiumrole(ctx: discord.Interaction, *, role: discord.Role):
    with open("config.json", "r") as f:
        config = json.load(f)
    owners = config["owners"]
    if int(ctx.user.id) in owners:
        config["premium-users-role"] = role.id
        with open("config.json", "w") as f:
            json.dump(config, f, indent=4)
        await ctx.response.send_message(f"Premium role has been set to {role.mention}")
    else:
        await ctx.response.send_message("unauthorized")

@client.tree.command(description="Ban a user and sync ban across all guilds.", name="add_ban")
async def ban_user(ctx: discord.Interaction, *, user: discord.User):
    with open("config.json", "r") as f:
        config = json.load(f)
    owners = config["owners"]
    if int(ctx.user.id) in owners:
        with open("bans.json", "r") as bans_file:
            bans_data = json.load(bans_file)   
        bans_data["banned_ids"].append(int(user.id)) 
        with open("bans.json", "w") as bans_file:
            json.dump(bans_data, bans_file, indent=4)    
        try:
            guild = ctx.guild
            await guild.ban(user, reason=f"Banned by {ctx.user.mention}")
            await ctx.response.send_message(f"{user} has been banned")
        except discord.Forbidden:
            await ctx.response.send_message("I do not have permission to ban users in this guild.")
    else:
        await ctx.response.send_message("Unauthorized")

@client.tree.command()
async def remove_ban(ctx: discord.Interaction, *, user: discord.User):
    with open("config.json", "r") as f:
        config = json.load(f)
    owners = config["owners"]
    if int(ctx.user.id) in owners:
        with open("bans.json", "r") as bans_file:
            bans_data = json.load(bans_file)   
        bans_data["banned_ids"].remove(int(user.id)) 
        with open("bans.json", "w") as bans_file:
            json.dump(bans_data, bans_file, indent=4)    
        try:
            guild = ctx.guild
            await guild.unban(user, reason=f"Unbanned by {ctx.user.mention}")
            await ctx.response.send_message(f"{user} has been unbanned")
        except discord.Forbidden:
            await ctx.response.send_message("I do not have permission to unban users in this guild.")
    else:
        await ctx.response.send_message("Unauthorized")

@client.tree.command(description="Sync ban users", name="ban_sync")
async def syncban(ctx: discord.Interaction):
    with open("config.json", "r") as f:
        config = json.load(f)
    owners = config["owners"]
    if int(ctx.user.id) in owners:
        with open("bans.json", "r") as bans_file:
            bans_data = json.load(bans_file)
        banned_ids = bans_data["banned_ids"]
        for guild in client.guilds:
            for user_id in banned_ids:
                user = client.get_user(user_id)
                if user:
                    try:
                        await guild.ban(user, reason="Sync bans")
                    except discord.Forbidden:
                        print(f"Cannot ban user {user} in guild {guild.name}.")
        await ctx.response.send_message("Sync ban completed across all guilds.")
    else:
        await ctx.response.send_message("Unauthorized")

@client.tree.command()
async def addslot(ctx: discord.Interaction, user: discord.User, *, channel_name: str):
    if ctx.user.guild_permissions.manage_channels:
        channel = discord.utils.get(ctx.user.guild.channels, name=channel_name)
        if not channel:
          await ctx.response.send_message(f"Channel `{channel_name}` not found." , ephemeral=True)
          return
        with open("slots.json", "r") as f:
            slot_data = json.load(f)
        slot_data[str(user.id)] = channel.name
        with open("slots.json", "w") as f:
            json.dump(slot_data, f, indent=4)
        await ctx.response.send_message(f"Added {user.mention}'s slot channel!")
        log_content = f"Added {user.mention} to slot database with channel {channel.name}"
        sendLogs(var["slot-webhook"], embed=True, content=log_content)
    else:
        await ctx.response.send_message("unauthorized")

@client.tree.command()
async def remove_slot(ctx: discord.Interaction, *, user: discord.User):
    with open("config.json", "r") as f:
        config = json.load(f)
    owners = config["owners"]  
    if int(ctx.user.id) in owners:
        with open("slots.json", "r") as f:
            slot_data = json.load(f)  
        if str(user.id) in slot_data:
            del slot_data[str(user.id)]
            with open("slots.json", "w") as f:
                json.dump(slot_data, f, indent=4)          
            await ctx.response.send_message(f"Removed {user.mention}'s slot channel.")
            ok = f"Removed {user.mention} from the slot database"
            sendLogs(var["slot-webhook"], embed=True, content=ok)
        else:
            await ctx.response.send_message(f"{user.mention} doesn't have a slot channel assigned.")
    else:
         await ctx.response.send_message("unauthorized")

@client.event
async def on_guild_channel_create(channel: discord.TextChannel):
    now = datetime.now().strftime("%H:%M:%S")
    if channel.category_id == category_id:
        time.sleep(1)
        async for messages in channel.history(limit=100):
            if messages.author.bot:
                for member in messages.mentions:
                  mem = channel.guild.get_member(int(member.id))
                  if mem is not None:
                    if int(mem.id) in blacklisted:
                        await channel.send(f"[{now}] | {mem.mention} you're blacklisted, deleting channel.")
                        time.sleep(5)
                        await channel.delete()
                    else:
                        headers = {"authorization": utoken, "Content-Type": 'application/json'}
                        r = requests.get(f'https://discord.com/api/v9/users/{member.id}/profile', headers=headers)
                        req = r.json()
                        if vanity in req['user_profile']['bio'].strip():
                            role_obj = discord.utils.get(channel.guild.roles, id=newbiesrole)
                            if role_obj is not None:
                                await mem.add_roles(role_obj)
                                sendLogs(huk, True, f"{member.mention} got newbie seller role.")
                                await channel.send(f"[{now}]: {member.mention} you got the seller role.")
                                time.sleep(5)
                                await channel.delete()
                            else:
                                print(f"Role with id {role} not found.")
                        else:
                            await channel.send(f"[{now}]: {member.mention} | Failed To Add Role")
                            await channel.send(f"""
>>> **HELP MESSAGE**

1. Add `{vanity}` in your **about me**
2. Close this ticket
3. Re Open ticket

Note: Ticket will self-destruct in fe seconds of inactivity.""")
                            time.sleep(5)
                            await channel.delete()
    elif channel.category_id == slot_access_category:
        async for messages in channel.history(limit=100):
            if messages.author.bot:
                for member in messages.mentions:
                    mem = channel.guild.get_member(int(member.id))
                    if int(mem.id) in blacklisted:
                        await channel.send(f"[{now}] | {mem.mention} you're blacklisted, deleting channel.")
                        await asyncio.sleep(5)
                        await channel.delete()
                    else:
                        await channel.send(f"[{now}]: Fetching slot....")
                        with open("slots.json", "r") as f:
                            slot_data = json.load(f)
                        role = channel.guild.get_role(premium_users_role)
                        user_id = str(mem.id)
                        if user_id in slot_data:
                            slot_name = slot_data[user_id]
                            existing_slot_channel = discord.utils.get(channel.guild.channels, name=slot_name)
                            if existing_slot_channel:
                                await existing_slot_channel.set_permissions(mem, read_messages=True, send_messages=True, mention_everyone=True)
                            if role is not None and mem is not None:
                                await channel.send(f"Added {role.mention} to {mem.mention}\nSuccessfully Assigned {mem.mention} to {existing_slot_channel.mention}.")
                                await mem.add_roles(role)
                                embed = discord.Embed(description=f"Added {role.mention} to {mem.mention}\nSuccessfully Added {mem.mention} to slot.")
                                await existing_slot_channel.send(embed=embed)
                            else:
                                await channel.send(f"No slots found.")
                        else:
                            await channel.send(f"No slots found for {mem.mention}.")

client.run(token, reconnect=True)
