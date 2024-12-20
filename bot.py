import asyncio
import discord
from discord.ext import commands
from discord import app_commands
import os
import scraper_functions

#Proper replacements made to create search term on given movie string
def create_search_term(movie_title):
    search_term = movie_title.replace(" ", "+")
    search_term = search_term.replace(":", "%3A")
    search_term = search_term.replace("/", "-")

    return search_term

class PaginationView(discord.ui.View):
    current_page : int = 0
    movie_embeds = {}

    def __init__(self, original_user, data):
        super().__init__(timeout=60)
        self.original_user = original_user
        self.data = data

    async def on_timeout(self):
        self.clear_items()
        await self.update_buttons()
        if self.message:
            await self.message.edit(view=self)

    # Creates an embed of current movie being viewed on page
    def get_movie_embed(self, data, current_page):
        movie_embed_attributes = (scraper_functions.scrape_website(data[current_page]))
        movie_embed = discord.Embed(title=f'{movie_embed_attributes[1]} • ({str(movie_embed_attributes[3])})', description=movie_embed_attributes[5], url=data[current_page])
        movie_embed.add_field(name="Director", value=movie_embed_attributes[2], inline=True)
        movie_embed.add_field(name="Runtime", value=movie_embed_attributes[4], inline=True)
        if movie_embed_attributes[7] != "N/A":
            movie_embed.add_field(name="Rating", value=f'{movie_embed_attributes[6]} from {movie_embed_attributes[7]} ratings', inline=True)
        else:
            movie_embed.add_field(name="Rating", value=f'{movie_embed_attributes[6]}', inline=True)
        if movie_embed_attributes[0] is None:
            movie_embed.set_thumbnail(url="https://i.imgur.com/pD7QZZ1.jpeg")
        else:
            movie_embed.set_thumbnail(url=movie_embed_attributes[0])
        movie_embed.set_footer(text=f"Page {self.current_page + 1}/{len(self.data)}")
        return movie_embed

    async def send(self, ctx):
        self.message = await ctx.send(view=self)
        try:
            await asyncio.wait_for(self.update_message(self.data,),timeout=30)
        except asyncio.TimeoutError:
            self.stop()

    async def update_message(self, data):
        await self.update_buttons()
        await self.message.edit(embed = self.get_movie_embed(data, self.current_page), view=self)

    async def update_buttons(self):
        if self.current_page == 0:
            self.first_page_button.disabled = True
            self.prev_button.disabled = True
            self.first_page_button.style = discord.ButtonStyle.gray
            self.prev_button.style = discord.ButtonStyle.gray
        else:
            self.first_page_button.disabled = False
            self.prev_button.disabled = False
            self.first_page_button.style = discord.ButtonStyle.green
            self.prev_button.style = discord.ButtonStyle.primary

        if self.current_page == len(self.data)-1:
            self.next_button.disabled = True
            self.last_page_button.disabled = True
            self.last_page_button.style = discord.ButtonStyle.gray
            self.next_button.style = discord.ButtonStyle.gray
        else:
            self.next_button.disabled = False
            self.last_page_button.disabled = False
            self.last_page_button.style = discord.ButtonStyle.green
            self.next_button.style = discord.ButtonStyle.primary

    #Checks if interaction belongs to user, if not they cannot use arrow buttons
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.original_user.id:
            await interaction.response.send_message("Only user who used /search_movie can use these.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label = "|<", style=discord.ButtonStyle.primary)
    async def first_page_button(self, interaction:discord.Interaction, button: discord.ui.Button):
        if await self.interaction_check(interaction):
            await interaction.response.defer()
            self.current_page = 0
            await self.update_message(self.data)

    @discord.ui.button(label = "Prev", style=discord.ButtonStyle.primary)
    async def prev_button(self, interaction:discord.Interaction, button: discord.ui.Button):
        if await self.interaction_check(interaction):
            await interaction.response.defer()
            if self.current_page != 0:
                self.current_page -= 1
            await self.update_message(self.data)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary)
    async def next_button(self, interaction:discord.Interaction, button: discord.ui.Button):
        if await self.interaction_check(interaction):
            await interaction.response.defer()
            if self.current_page != len(self.data)-1:
                self.current_page += 1
                if self.current_page not in self.movie_embeds:
                    new_embed = self.get_movie_embed(self.data, self.current_page)
                    self.movie_embeds[self.current_page] = new_embed
            await self.update_message(self.data)

    @discord.ui.button(label = ">|", style=discord.ButtonStyle.primary)
    async def last_page_button(self, interaction:discord.Interaction, button: discord.ui.Button):
        if await self.interaction_check(interaction):
            await interaction.response.defer()
            self.current_page = int(len(self.data) - 1)
            if self.current_page not in self.movie_embeds:
                new_embed = self.get_movie_embed(self.data, self.current_page)
                self.movie_embeds[self.current_page] = new_embed
            await self.update_message(self.data)

def run_discord_bot():
    TOKEN = str(os.environ.get('LetterboxdBot_TOKEN'))
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix='/', intents=intents)

    @bot.event
    async def on_ready():
        print(f'{bot.user} is now running!')
        try:
            synced = await bot.tree.sync()  # guild = discord.Object(id = 518631948197822465))
            print(f"Synced {len(synced)} command(s)")
        except Exception as e:
            print(e)

    @bot.tree.command(name="search_movie", description="Searches for a movie on letterboxd")
    @app_commands.describe(movie_title="movie that will be searched on letterboxd")
    async def search_movie(interaction: discord.Interaction, movie_title: str):
        search_term = create_search_term(movie_title)
        search_term_links = scraper_functions.get_search_term_urls(search_term)
        ctx = await bot.get_context(interaction)

        #If list then there are valid links that have been found
        if isinstance(search_term_links, list):
            pagination_view = PaginationView(original_user=interaction.user, data=search_term_links)
            await pagination_view.send(ctx)
        elif search_term_links is None:
            await interaction.response.send_message('NO RESULTS. There were no matches for your search term. Make sure you are entering a valid movie title.')
        else:
            await interaction.response.send_message(search_term_links)
    
    bot.run(TOKEN)
