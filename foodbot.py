import json
import discord 
import os 
import time 
from discord.ext import commands, tasks

token = "" #Put in your bot token type = string
admins = [] #Put in your Discord User ID. Seperate by comma if you want to give multiple accounts admin permissions for the bot
botid = 0 #copy the id of your bot in there type = int




#discord permissions 
intents = discord.Intents.default()
intents.members = True

current_user = 0

#command prefix
command_prefix = "!"
client = commands.Bot(command_prefix=command_prefix, intents=intents)

client.remove_command('help') 


def load_recipes():
	global recipes
	with open("recipes.json") as f:
		recipes = json.loads(f.read())

def save_recipes():
	with open("recipes.json","w+") as f:
		f.write(json.dumps(recipes))

try:
	load_recipes()
except:
	save_recipes()
	load_recipes()

#on_ready function
@client.event
async def on_ready():
	print("logged in as:")
	print(client.user.name)

#display helpful commands WIP: Tutorial, extended description, usage !help {command} > ...
@client.command()
async def help(ctx,*,message="}||{"):
	if message.upper() != "EXAMPLE":
		embed = discord.Embed(colour = discord.Colour.green())	
		embed.set_author(name='Commands:')
		embed.add_field(name=f'{command_prefix}recipe', value=f"Lists available recipes for your ingredients. Usage : '{command_prefix}recipe "+"{ingredients}'",inline=False)
		embed.add_field(name=f'{command_prefix}add_recipe', value=f"Adds a Recipe. Usage : '{command_prefix}add_recipe" +" {name:ingredients:tags}' must include name, ingredients",inline=False)
		embed.add_field(name=f'{command_prefix}allrecipes', value=f"Displays all recipes. Usage : '{command_prefix}allrecipes'",inline=False)
		embed.add_field(name=f'{command_prefix}edit', value=f"Edits a recipe. Usage : '{command_prefix}edit "+"{recipe}'",inline=False)
		embed.add_field(name=f'{command_prefix}edit', value=f"Displays how to make the specified recipe. Usage : '{command_prefix}howtomake "+"{recipe}'",inline=False)
		embed.add_field(name=f'{command_prefix}find', value=f"Find one or more recipes. Usage : '{command_prefix}find "+"{tags:ingredients} must have either tags or ingredient'",inline=False)
		embed.add_field(name=f'{command_prefix}shopping_list', value=f"Sends YOU a list with all the ingredients you need for a recipe. Usage : '{command_prefix}shopping_list "+"{recipe}'",inline=False)
		embed.add_field(name=f'{command_prefix}have', value=f'Displays all recipes you can make with your specified ingredients. Usage : '+command_prefix+"'have {ingredients}'",inline=False)

		await ctx.channel.send(embed=embed)

#todolist
#sort available recipes by amount and make only top X, default show top 10 or top 5 recipes 
#tell everyone what they're missing when deciding for a recipe with specified ingredients


@client.command()
async def allrecipes(ctx,*,message=""):
	embed = discord.Embed(colour = discord.Colour.dark_gold())
	temp = ""
	for recipe in recipes:
		temp+= recipes[recipe]["name"]+"\n"

	embed.add_field(name='Available recipes are:', value=temp,inline=False)

	await ctx.channel.send(embed=embed)


@client.command()
async def find(ctx,*,message):
	available_recipes = []
	tags,ingr = ["any"],["any"]
	message = message.split(":")
	if len(message) == 2:
		if message[0] != "":
			
			ingr = message[0].split(" ")

		if message[1] != "":
			tags = message[1].split(" ")
	else:
		ingr = message[0].split(" ")

	if tags == ["any"] and ingr != ["any"]:
		for recipe in recipes:
			for ingredient in ingr:
				if ingredient in recipes[recipe]["ingredients"]:
					available_recipes.append(recipes[recipe]["name"])

	elif ingr == ["any"] and tags != ["any"]:
		for recipe in recipes:
			for tag in tags:
				if tag in recipes[recipe]["tags"]:
					available_recipes.append(recipes[recipe]["name"])
	else:
		for recipe in recipes:
			for tag in tags:
				if tag in recipes[recipe]["tags"]:
					for ingr in recipes[recipe]["ingredients"]:
						available_recipes.append(recipes[recipe]["name"])
	available_recipes = list(set(available_recipes))
	temp = ""
	for recipe in available_recipes:
		temp+= recipe+"\n"
	embed = discord.Embed(colour = discord.Colour.gold())
	if len(available_recipes) != 0:
		if len(available_recipes) == 1:
			embed.add_field(name='I have found this recipe for you!', value=temp,inline=False)

		else:
			embed.add_field(name='I have found these recipes for you!', value=temp,inline=False)
		await ctx.channel.send(embed=embed)
	else:
		await ctx.send("WOA! Looks like I don't have any recipes available with your ingredients or tags..")

temp_recipe = {

	"empty" : 
	{
		"name" : "",
		"ingredients" : [],
		"tags" : [],
		"description" : ""
	}
}

@client.event
async def on_message(command):
	message = command.content
	if command.author.id == botid:
		return
	if message.startswith('!edit'):
		channel = command.channel
		try:
			if command.author.id not in admins:
				await channel.send("Yikes! Looks like you're missing permission to use that command.")
				await channel.send("If you believe this is a mistake, message one of the moderators about this.")
				return
			if len(message.split(" ")) == 1:
				await channel.send("You haven't specified a recipe!")
				return
			global current_user
			current_user = command.author.id
			message = message.split(" ")
			message.pop(0)
			recipe = ""
			for st in message:
				recipe += st + " "
			recipe = recipe.strip()
			av = False
			for _ in recipes:
				if _ == recipe:
					av = True
			if av == False:
				await channel.send(f'Your specified recipe "{recipe}" does not exist.')
				await channel.send("If you would like to add it use the !add_recipe command or ask one of the moderators for help")
				return
			await channel.send("What category would you like to change? name | ingredients | tags | description | remove recipe ")
			category = await client.wait_for("message")
			if category.content != current_user:return
			category = category.content
			if category == "remove recipe":
				await channel.send(f'Recipe {recipe} has been successfully removed.')
				recipes.pop(recipe)
				return
			if category in ["description","name"]: kind = "string"
			elif category in ["ingredients","tags"]: kind = "array" 
			else:
				await channel.send(f'Category "{category}" does not exist.')
				return

			await channel.send("Choose a mode: edit | add | remove ")
			mode = await client.wait_for("message")
			if mode.content != current_user:return
			mode = mode.content
			if mode == "remove":
				recipes[recipe][category] = temp_recipe["empty"][category]
				await channel.send(f'Category "{category}" for {recipe} has been successfully removed.')
				return
			else:
				new = await client.wait_for("message")
				if new.content != current_user:return
				new = new.content

			if kind == "array":
				temp = []
				new = new.split(" ")
				for string in new:
					temp.append(string)
				new = temp
		
			if mode == "remove" and category == "name":
				await channel.send("You cannot remove the name of a recipe!")
				return

			if mode == "edit":
				
				if category == "name":

					recipes.update({new : {"name" : new, "ingredients" : recipes[recipe]["ingredients"],"tags" : recipes[recipe]["tags"],"description" : recipes[recipe]["description"]}})
					recipes.pop(recipe)
					return
				if kind == "string":
					recipes[recipe][category] = new
					return
				elif kind == "array":
					recipes[recipe][category] = [k for k in new]
					return

			elif mode == "add":
				if kind == "string":
					if category == "name":
						recipes.update({recipes[recipe]["name"]+new : {"name" : recipes[recipe]["name"]+new, "ingredients" : recipes[recipe]["ingredients"],"tags" : recipes[recipe]["tags"],"description" : recipes[recipe]["description"]}})
						recipes.pop(recipe)
						return

				elif kind == "array":
					for element in new:
						recipes[recipe][category].append(element)
					return

			else:
				await channel.send(f'Mode "{mode}" does not exist.')
				return

		except:
			await channel.send("Yikes! Looks like something went wrong here. Try again later, if the error still occurs proceed to message a moderator about the issue.")
	
	else: await client.process_commands(command)


"""
Making use of the "Ottolenghi Simple" recipe book / website by redirecting to a page/site for a given recipe (WIP)
@client.command()
async def simple(ctx,*,message):
	try:
		recipe = recipes[recipe]["simple"]
		if recipe != None: await ctx.send(recipe)
	except:
		recipes[recipe].update({"simple" : None})
"""

@client.command()
async def shopping_list(ctx,*,message : str):
	ingredients = ""
	for ingr in recipes[message]["ingredients"]:
		ingredients += ingr + "\n"
	
	embed = discord.Embed(colour = discord.Colour.green())
	embed.add_field(name="Your shopping list:",value=ingredients,inline=False)

	await ctx.author.send(embed=embed)


#Will soon be reworked in the !edit command style
@client.command()
async def add_recipe(ctx,*,message):
	if ctx.author.id not in admins:
		return
	ingr_list = []
	taglist = []
	name_temp = ""
	try:
		name = message.split(":")[0]
		name = name.split("_")
		for word in name:
			name_temp += word.capitalize()+" "
		name = name_temp.strip()

		ingredients = message.split(":")[1]
	except:
		name = "pasta"
		ingredients = "noodles"
	tags = ""
	try:
		tags = message.split(":")[2]
	except:
		pass
	ingredients = ingredients.split(" ")
	for ingredient in ingredients:
		if ingredient != None and ingredient != "":
			ingr_list.append(ingredient)

	tags = tags.split(" ")
	for tag in tags:
		if tag != None and tag != "":
			taglist.append(tag)

	#descriptions have to be added using the !edit command
	recipes.update({name : {"name" : name, "ingredients" : ingr_list,"tags" : taglist, "description" : ""}})
	save_recipes()
	load_recipes()

for recipe in recipes:
	try:
		recipes[recipe]["description"]
	except:
		recipes[recipe].update({"description" : "UWU"})

@client.command()
async def save(ctx):
	save_recipes()

@client.command()
async def load(ctx):
	load_recipes()


@client.command()
async def howtomake(ctx,*,message):
	recipe = recipes[message.strip()]
	name = recipe["name"]
	ingredients = recipe["ingredients"]
	description = recipe["description"]
	temp = ""
	for ing in ingredients:
		temp += ing +", "
	ingredients = temp[0:-2]

	description = recipe["description"]
	embed = discord.Embed(colour = discord.Colour.dark_blue())
	embed.add_field(name=f'You need {ingredients}!', value=f'{description}', inline = False)
	await ctx.send(embed=embed)


@client.command()
async def need(ctx,*,message):
	ingredients = ""
	for ingr in recipes[message]["ingredients"]:
		ingredients += ingr + "\n"
	
	embed = discord.Embed(colour = discord.Colour.green())
	embed.add_field(name=f"For {message.strip()} you need:",value=ingredients,inline=False)
	await ctx.send(embed=embed)


@client.command()
async def have(ctx,*,message):
	available_recipes = []
	message = message.split(" ")
	for recipe in recipes:
		recipe_available = True
		for ingredients in recipes[recipe]["ingredients"]:
			if ingredients not in message:
				recipe_available = False
		if recipe_available == True:
			available_recipes.append(recipes[recipe]["name"])
	if len(available_recipes) != 0:

		temp = ""
		for re in available_recipes:
			temp+= re+"\n" 

		embed = discord.Embed(colour = discord.Colour.gold())

		if len(available_recipes) == 1:
			embed.add_field(name='I have found this recipe for you!', value=temp,inline=False)
		else:
			embed.add_field(name='I have found these recipes for you!', value=temp,inline=False)

		await ctx.channel.send(embed=embed)

	else:
		await ctx.send("WOA! Looks like I don't have any recipes available with your ingredients..")


client.run(token)
