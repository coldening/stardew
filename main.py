import discord, os, random, time
from discord import app_commands
from discord.ext import commands
from replit import db

bot = commands.Bot(command_prefix="-", intents=discord.Intents.all())

def giveItem(interaction, iid, iws, c):
  if iid in db[str(interaction.user.id)]['inv']:
    db[str(interaction.user.id)]['inv'][iid]["count"] = db[str(interaction.user.id)]['inv'][iid]["count"] + c
  else:
    iws["count"] = c
    db[str(interaction.user.id)]['inv'][iid] = iws

def fixShop():
  db["shop"] = {"turnip_seed":{"name": "Turnip", "description": "A stardew classic, go and plant it on your farm!", "value": 30, "type": "seed", "count": 1, "emoji": "Seeds :seedling:"},"onion_seed":{"name": "Onion", "description": "High risk and reward crop.", "value": 100, "type": "seed", "count": 1, "emoji": "Seeds :beans:"},"farm_pass":{"name": "Farming Pass", "description": "Get another Farm Slot. (up to 10)", "value": 1000, "type": "tool", "count": 1, "emoji": ":tickets:"},"starter_pickaxe":{"name": "Starter Pickaxe", "description": "Start mining for some extra money.", "value": 1500, "type": "pick", "count": 1, "emoji": ":pick:"}}

@bot.event
async def on_ready():
  print("Stardew Ready:")
  fixShop()
  try:
    synced = await bot.tree.sync()
    print(f"Synced {len(synced)} commands!")
  except Exception as e:
    print(f"Error syncing commands: {e}")

@bot.event
async def on_message(message):
  if message.author == bot.user:
    return
  
  knownUser = False
  keys = db.keys()
  if str(message.author.id) in keys:
    knownUser = True
  else:
    db[str(message.author.id)] = {"balance": 100000, "inv": {"watering_can": {"name": "Watering Can", "description": "A simple watering can!", "value": -1, "type": "tool", "count": 1, "emoji": ":sweat_drops:"}}, "farm": ["0None","0None","0None"], "wcts": 0, "mts": 0}

@bot.tree.command(name="fixshop")
async def fixshop(interaction: discord.Interaction):
  fixShop()
  await interaction.response.send_message("This command has tried to repair shops.",ephemeral=True)

@bot.tree.command(name="leak")
@app_commands.describe(who = "whos ip should i leak")
async def leak(interaction: discord.Interaction, who: str):
  await interaction.response.send_message(f"{who}'s ip is: {random.randint(10,255)}.{random.randint(10,255)}.{random.randint(10,255)}.{random.randint(10,255)}")

@bot.tree.command(name="wipe",description="wipe the database")
async def wipe(interaction: discord.Interaction):
  if str(interaction.user.id) == "553747931736440834":
    await interaction.response.send_message("Wiped DB!",ephemeral=True)
    for key in db.keys():
      del db[key]
  else:
    await interaction.response.send_message("no screw you!!1!!1!1!1 (you are not the lego.ninjago on fiscord1)",ephemeral=True)

@bot.tree.command(name="stats",description="view your stats.")
async def stats(interaction: discord.Interaction):
  embed = discord.Embed(title="**Stats**", color=discord.Color.blue())
  embed.add_field(name="**Balance**",value=f"{db[str(interaction.user.id)]['balance']} Gold",inline=True)
  embed.add_field(name="**Farm Slots**",value=f"{len(db[str(interaction.user.id)]['farm'])}",inline=True)
  await interaction.response.send_message(embed = embed,ephemeral=True)

@bot.tree.command(name="shop",description="check the shop!")
async def shop(interaction:discord.Interaction):
  embed = discord.Embed(title="**Shop**",color=discord.Color.red())
  for item, value in db["shop"].items():
    sv = value['value']
    sv = str(sv)
    if sv == -1:
      sv = "Can't Sell"
    else:
      sv += " Gold"
    embed.add_field(name=f"**{value['name']} {value['emoji']}** ({value['type']})",value=f"{value['description']}\n**Price: {sv}**")
  await interaction.response.send_message(embed=embed,ephemeral=True)

@bot.tree.command(name="inv",description="check your inventory!")
async def inv(interaction:discord.Interaction):
  embed = discord.Embed(title="**Inventory**",color=discord.Color.red())
  for item, value in db[str(interaction.user.id)]["inv"].items():
    sv = value['value']
    sv = str(sv)
    if sv == "-1":
      sv = "Can't Sell"
    else:
      sv += " Gold"
    embed.add_field(name=f"**{value['name']} {value ['emoji']}** x{value['count']}",value=f"{value['description']}\n\n**{sv}**\n({value['type']})")
  await interaction.response.send_message(embed=embed,ephemeral=True)

@bot.tree.command(name="farm",description="view or use your farm!")
async def farm(interaction: discord.Interaction):
  embed = discord.Embed(title="**Farm**",color=discord.Color.green())
  i = 0
  slots = db[str(interaction.user.id)]["farm"]
  while i < len(slots):
    sat = slots[i]
    if slots[i] == None:
      sat = "0None"
    stage = sat[0:1]
    type = sat[1:]
    semo = ""
    if stage == "1":
      semo = "Seed :seedling:"
    if stage == "2":
      semo = "Sprout :potted_plant:"
    if stage == "3":
      semo = "Plant :evergreen_tree:\n\n(Ready for Harvest)"
    i += 1
    embed.add_field(name=f"**Slot {i}**",value=f"{type} {semo}")
  await interaction.response.send_message(embed=embed,ephemeral=True)

@bot.tree.command(name="plant",description="plant a seed.")
async def plant(interaction: discord.Interaction, item: str, slot: int):
  farm = db[str(interaction.user.id)]["farm"]
  try:
    if farm[slot-1] == "0None":
      iis = False
      iws = {}
      iid = 0
      for id, value in db[str(interaction.user.id)]["inv"].items():
        if value["name"] == item and value["type"] == "seed":
          iis = True
          iws = value
          iid = id
      if iis == True:
        db[str(interaction.user.id)]['inv'][iid]["count"] = db[str(interaction.user.id)]['inv'][iid]["count"] - 1
        if db[str(interaction.user.id)]['inv'][iid]["count"] <= 0:
          del db[str(interaction.user.id)]['inv'][iid]
        db[str(interaction.user.id)]['farm'][slot-1] = f"1{iws['name']}"
        await interaction.response.send_message(f"You just placed down a {iws['name']} at slot {slot}!",ephemeral=True)
      else:
        await interaction.response.send_message("Sorry, but that is not a valid seed.",ephemeral=True)
    else:
      await interaction.response.send_message("Sorry, but that is not a valid spot.",ephemeral=True)
  except:
    await interaction.response.send_message("Sorry, but that is not a valid spot/seed.",ephemeral=True)

@plant.autocomplete("item")
async def plant_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
  data = []
  for item, value in db[str(interaction.user.id)]["inv"].items():
    if value["type"] == "seed":
      data.append(app_commands.Choice(name=value["name"],value=value["name"]))
  return data

@bot.tree.command(name="use",description="use an item.")
async def use(interaction: discord.Interaction, item: str):
  iis = False
  iws = {}
  iid = 0
  for id, value in db[str(interaction.user.id)]["inv"].items():
    if value["name"] == item and value["type"] == "tool" or "pick":
      iis = True
      iws = value
      iid = id
  if iis == True:
    if iws["type"] == "pick":
      if time.time() >= db[str(interaction.user.id)]["mts"]:
        cd = 60
        db[str(interaction.user.id)]["mts"] = time.time()
        txt = "Heres your loot from mining:"
        await interaction.response.send_message(txt,ephemeral=True)
      else:
        await interaction.response.send_message(f"Sorry, but you can only use the {iws['name']} <t:{mts}:R>",ephemeral=True)
    if iws["name"] == "Farming Pass":
      if len(db[str(interaction.user.id)]["farm"]) < 10:
        db[str(interaction.user.id)]["farm"].append("0None")
        await interaction.response.send_message("Used Farming Pass!",ephemeral=True)
        db[str(interaction.user.id)]['inv']["farm_pass"]["count"] = db[str(interaction.user.id)]['inv']["farm_pass"]["count"] - 1
        if db[str(interaction.user.id)]['inv']["farm_pass"]["count"] <= 0:
          del db[str(interaction.user.id)]['inv']["farm_pass"]
      else:
        await interaction.response.send_message("You already have 10 Farm Slots.",ephemeral=True)
    if iws["name"] == "Watering Can":
      if time.time() >= db[str(interaction.user.id)]["wcts"]:
        await interaction.response.send_message("Used Watering Can!",ephemeral=True)
        db[str(interaction.user.id)]["wcts"] = time.time() + 120
      i = 0
      farm = db[str(interaction.user.id)]["farm"]
      while i < len(farm):
        if farm[i] != "0None":
          fi = farm[i]
          stage = fi[0:1]
          type = fi[1:]
          stage = int(stage)
          if stage < 3:
            stage += 1
          db[str(interaction.user.id)]["farm"][i] = f"{stage}{type}"
        i += 1
      else:
        wcts = int(db[str(interaction.user.id)]["wcts"])
        await interaction.response.send_message(f"Sorry, but you can only use the Watering Can <t:{wcts}:R>",ephemeral=True)
  else:
    await interaction.response.send_message("Sorry, but that is not a valid tool.",ephemeral=True)

@use.autocomplete("item")
async def use_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
  data = []
  for item, value in db[str(interaction.user.id)]["inv"].items():
    if value["type"] == "tool" or "pick":
      data.append(app_commands.Choice(name=value["name"],value=value["name"]))
  return data

@bot.tree.command(name="buy",description="buy an item.")
async def buy(interaction: discord.Interaction, item: str, count: int):
  iis = False
  price = 0
  iws = 0
  iid = 0
  for id, value in db["shop"].items():
    if value["name"] == item:
      iis = True
      price = value["value"] * count
      iws = value
      iid = id
  if iis == True:
    if db[str(interaction.user.id)]['balance'] >= price:
      bal = db[str(interaction.user.id)]['balance'] - price
      db[str(interaction.user.id)]['balance'] = bal
      giveItem(interaction, iid, iws, count)
      await interaction.response.send_message(f"You bought {count}x {item} for {price} Gold!",ephemeral=True)
    else:
      await interaction.response.send_message("Sorry, but you don't have enough gold for that item.",ephemeral=True)
  else:
    await interaction.response.send_message("Sorry, but that is not a valid item.",ephemeral=True)

@buy.autocomplete("item")
async def buy_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
  data = []
  for item, value in db["shop"].items():
      data.append(app_commands.Choice(name=value["name"],value=value["name"]))
  return data

@bot.tree.command(name="harvest",description="harvest any fully grown crops.")
async def harvest(interaction: discord.Interaction):
  await interaction.response.send_message("Harvested every crop that was ready!",ephemeral=True)
  i = 0
  farm = db[str(interaction.user.id)]['farm']
  while i < len(farm):
    if farm[i].__contains__("3"):
      product = farm[i][1:]
      if product == "Turnip":
        giveItem(interaction, "turnip", {"name": "Grown Turnip", "description": "Nice and grown, the perfect first crop.", "value": 70, "type": "material", "count": 1, "emoji": ":purple_heart:"}, random.randint(1,3))
      if product == "Onion":
        giveItem(interaction, "onion", {"name": "Grown Onion", "description": "Not worth much on it's own.", "value": 16, "type": "material", "count": 1, "emoji": ":onion:"}, random.randint(14,32))
      db[str(interaction.user.id)]['farm'][i] = "0None"
    i += 1

@bot.tree.command(name="sell",description="sell an item.")
async def sell(interaction: discord.Interaction, item: str, count: int):
  iis = False
  iws = {}
  iid = 0
  for id, value in db[str(interaction.user.id)]["inv"].items():
    if value["name"] == item and value["value"] != -1:
      iis = True
      iws = value
      iid = id
  if iis == True:
    if count > db[str(interaction.user.id)]['inv'][iid]["count"]:
      count = db[str(interaction.user.id)]['inv'][iid]["count"]
    db[str(interaction.user.id)]['inv'][iid]["count"] = db[str(interaction.user.id)]['inv'][iid]["count"] - count
    if db[str(interaction.user.id)]['inv'][iid]["count"] <= 0:
      del db[str(interaction.user.id)]['inv'][iid]
    db[str(interaction.user.id)]['balance'] = db[str(interaction.user.id)]['balance'] + (count*value['value'])
    await interaction.response.send_message(f"You just sold {count}x {iws['name']} for {count*value['value']} Gold.",ephemeral=True)
  else:
    await interaction.response.send_message("Sorry, but that is not a valid item.",ephemeral=True)

@sell.autocomplete("item")
async def sell_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
  data = []
  for item, value in db[str(interaction.user.id)]["inv"].items():
    data.append(app_commands.Choice(name=value["name"],value=value["name"]))
  return data

@bot.tree.command(name="guide",description="a quick earlygame guide.")
async def guide(interaction: discord.Interaction):
  await interaction.response.send_message("**Guide**\n1. Plant a Turnip\n2. Use your watering can to grow every crop in your farm\n3. Harvest and sell your Turnip",ephemeral=True)

token = os.environ["TOKEN"]
bot.run(token)
