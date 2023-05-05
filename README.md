# LetterboxdBot Discord Bot
Invite to your Discord Server: https://discord.com/oauth2/authorize?client_id=1100138412238962810&permissions=2147510272&scope=bot

# Example
https://user-images.githubusercontent.com/70344759/236554071-3f740134-4123-48d3-9305-21dd2567fd8c.mov

# Description
Used to retrieve information about movies on https://letterboxd.com/ including:  
- Title 
- Poster
- Director 
- Release Year 
- Runtime 
- Description
- Average Movie Rating
- Review Count 

Movies should be entered as accurate as possible, spelling mistakes will not be accounted for/will cause your search to fail. At once a maximum of 20 results will be returned (the first page of Letterboxd) so if something more general is searched like the word "The" you probably won't find the movie you're looking for.


# Future Improvements:
- Currently information is retrieved using scraping (not ideal), if access is granted to Letterboxd API with a key then should be able to more easily retrieve information. One positive of using web scraping is that any user can download and customize this source code and use the bot for themselves, but with using the API this wouldn't be true.
- Adding previously searched movies to PostgreSQL Database for quicker data retrieval (This is without API access)
- Make code more modular
- Unit testing
- Add Cogs
