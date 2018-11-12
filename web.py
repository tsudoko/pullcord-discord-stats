#!/usr/bin/python3

import csv
from pathlib import Path
import os

from jinja2 import Environment, FileSystemLoader, select_autoescape
env = Environment(
    loader=FileSystemLoader('templates'),
    autoescape=select_autoescape(['html', 'xml'])
)

class Guild(): pass
class Channel(): pass

PULLCORD_DIR = "/home/sanqui/archive/discord/run"

IGNORE_GUILD_IDS = [139677590393716737, 272603653389549578]

guild_ids = [int(x.name) for x in Path(PULLCORD_DIR+"/channels").iterdir() if x.name != "@me"]

guilds = {}

for guild_id in guild_ids:
    if guild_id in IGNORE_GUILD_IDS: continue
    guild = Guild()
    guild.id = guild_id
    guilds[guild_id] = guild
    guild.channels = {}
    guild.members = []
    for row in csv.reader(open(f"{PULLCORD_DIR}/channels/{guild_id}/guild.tsv"), delimiter='\t'):
        time, fetchtype, action, type, id = row[0:5]
        data = row[5:]
        if type == "guild":
            keys = "name,icon,splash,ownerid,afkchanid,afktimeout,embeddable,embedchanid".split(',')
            for key, value in zip(keys, data):
                setattr(guild, key, value)
        elif type == "channel":
            keys = "chantype,pos,name,topic,nsfw,category,recipients,icon".split(',')
            channel = Channel()
            channel.id = id
            for key, value in zip(keys, data):
                setattr(channel, key, value)
            guild.channels[id] = channel
        elif type == "member":
            if action == "add":
                guild.members.append(id)
            elif action == "delete":
                guild.members.delete(id)
    
    guild.channels = dict(sorted(guild.channels.items(), key=lambda c: int(c[1].pos) + (1000 if c[1].chantype == "voice" else 0)))
    
    guild.filesize = 0
    for channel in Path(f"{PULLCORD_DIR}/channels/{guild_id}/").iterdir():
        size = os.stat(channel).st_size
        guild.filesize += size
    

       

guilds = dict(sorted(guilds.items()))
guild_sizes = {}

for guild_id, guild in guilds.items():
    #print(f"{guild.id} {guild.name} - {len(guild.channels)} channels, {len(guild.members)} members")
    guild_sizes[guild_id] = len(guild.channels) + len(guild.members)

max_guild_filesize = max(g.filesize for g in guilds.values())

template = env.get_template("index.html")
open("out/index.html", "w").write(template.render(guilds=guilds, guild_sizes=guild_sizes, max_guild_sizes = max(guild_sizes.values()),
    max_guild_filesize=max_guild_filesize,
    total_channels = sum(len(g.channels) for g in guilds.values()),
    total_members = sum(len(g.members) for g in guilds.values()),
    total_text_filesize = sum(g.filesize for g in guilds.values()),
))

    
