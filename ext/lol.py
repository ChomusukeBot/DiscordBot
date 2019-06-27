# Import the commands extension
import discord
from discord.ext import commands
import os
import requests
from cog import Cog
import json
import datetime

# Base URL for all API calls
BASE_URL = "https://{}.api.riotgames.com"
# League of Legends Static Data for profile pictures
PROFILE_IMAGE_URL = "http://ddragon.leagueoflegends.com/cdn/{}/img/profileicon/{}.png"
# League of Legends Static Data for champions
CHAMPIONS_URL = "http://ddragon.leagueoflegends.com/cdn/{}/data/en_US/champion.json"
# API Operation used to access summoner data
SUMMONER_API = "/lol/summoner/v4/summoners/by-name/{}?api_key={}"
# API Operation used to access summoner ranked data
RANKED_API = "/lol/league/v4/entries/by-summoner/{}?api_key={}"
# API Operation used to access summoner match history
MATCHES_API = "/lol/match/v4/matchlists/by-account/{}?api_key={}"
# API Operation used to access a specific match
MATCH_API = "/lol/match/v4/matches/{}?api_key={}"
# A .json file storing the current and all previous versions of league of legends
LEAGUE_VERSION = "https://ddragon.leagueoflegends.com/api/versions.json"
# A dictionary of RIOT's regional endpoints and their corresponding server shortcuts
REGIONS = {
    "br": "br1",
    "eune": "eun1",
    "euw": "euw1",
    "jp": "jp1",
    "kr": "kr",
    "lan": "la1",
    "las": "la2",
    "na": "na1",
    "oce": "oc1",
    "tr": "tr1",
    "ru": "ru",
    "pbe": "pbe1"
}
MATCHMAKING_QUEUES = {
    0:	"Custom game",
    2:	"Summoner's Rift - 5v5 Blind Pick game",
    4:	"Summoner's Rift - 5v5 Ranked Solo game",
    6:	"Summoner's Rift - 5v5 Ranked Premade game",
    7:	"Summoner's Rift - Co-op vs AI game",
    8:	"Twisted Treeline - 3v3 Normal game",
    9:	"Twisted Treeline - 3v3 Ranked Flex game",
    14:	"Summoner's Rift - 5v5 Draft Pick game",
    16:	"Crystal Scar - 5v5 Dominion Blind Pick game",
    17:	"Crystal Scar - 5v5 Dominion Draft Pick game",
    25:	"Crystal Scar - Dominion Co-op vs AI game",
    31:	"Summoner's Rift - Co-op vs AI Intro Bot game",
    32:	"Summoner's Rift - Co-op vs AI Beginner Bot game",
    33:	"Summoner's Rift - Co-op vs AI Intermediate Bot game",
    41:	"Twisted Treeline - 3v3 Ranked Team game",
    42:	"Summoner's Rift - 5v5 Ranked Team game",
    52:	"Twisted Treeline - Co-op vs AI game",
    61:	"Summoner's Rift - 5v5 Team Builder game",
    65:	"Howling Abyss - 5v5 ARAM game",
    67:	"Howling Abyss - ARAM Co-op vs AI game",
    70:	"Summoner's Rift - One for All game",
    72:	"Howling Abyss - 1v1 Snowdown Showdown game",
    73:	"Howling Abyss - 2v2 Snowdown Showdown game",
    75:	"Summoner's Rift - 6v6 Hexakill game",
    76:	"Summoner's Rift - Ultra Rapid Fire game",
    78:	"Howling Abyss - One For All: Mirror Mode game",
    83:	"Summoner's Rift - Co-op vs AI Ultra Rapid Fire game",
    91:	"Summoner's Rift - Doom Bots Rank 1 game",
    92:	"Summoner's Rift - Doom Bots Rank 2 game",
    93:	"Summoner's Rift - Doom Bots Rank 5 game",
    96:	"Crystal Scar - Ascension game",
    98:	"Twisted Treeline - 6v6 Hexakill game",
    100:	"Butcher's Bridge - 5v5 ARAM game",
    300:	"Howling Abyss - Legend of the Poro King game",
    310:	"Summoner's Rift - Nemesis game",
    313:	"Summoner's Rift - Black Market Brawlers game",
    315:	"Summoner's Rift - Nexus Siege game",
    317:	"Crystal Scar - Definitely Not Dominion game",
    318:	"Summoner's Rift - ARURF game",
    325:	"Summoner's Rift - All Random game",
    400:	"Summoner's Rift - 5v5 Draft Pick game",
    410:	"Summoner's Rift - 5v5 Ranked Dynamic game",
    420:	"Summoner's Rift - 5v5 Ranked Solo game",
    430:	"Summoner's Rift - 5v5 Blind Pick game",
    440:	"Summoner's Rift - 5v5 Ranked Flex game",
    450:	"Howling Abyss - 5v5 ARAM game",
    460:	"Twisted Treeline - 3v3 Blind Pick game",
    470:	"Twisted Treeline - 3v3 Ranked Flex game",
    600:	"Summoner's Rift - Blood Hunt Assassin game",
    610:	"Cosmic Ruins - Dark Star: Singularity game",
    700:	"Summoner's Rift - Clash game",
    800:	"Twisted Treeline - Co-op vs. AI Intermediate Bot game",
    810:	"Twisted Treeline - Co-op vs. AI Intro Bot game",
    820:	"Twisted Treeline - Co-op vs. AI Beginner Bot game",
    830:	"Summoner's Rift - Co-op vs. AI Intro Bot game",
    840:	"Summoner's Rift - Co-op vs. AI Beginner Bot game",
    850:	"Summoner's Rift - Co-op vs. AI Intermediate Bot game",
    900:	"Summoner's Rift - ARURF game",
    910:	"Crystal Scar - Ascension game",
    920:	"Howling Abyss - Legend of the Poro King game",
    940:	"Summoner's Rift - Nexus Siege game",
    950:	"Summoner's Rift - Doom Bots Voting game",
    960:	"Summoner's Rift - Doom Bots Standard game",
    980:	"Valoran City Park - Star Guardian Invasion: Normal game",
    990:	"Valoran City Park - Star Guardian Invasion: Onslaught game",
    1000:	"Overcharge	PROJECT: Hunters game",
    1010:	"Summoner's Rift - Snow ARURF game",
    1020:	"Summoner's Rift - One for All game",
    1030:	"Crash Site	Odyssey Extraction: Intro game",
    1040:	"Crash Site	Odyssey Extraction: Cadet game",
    1050:	"Crash Site	Odyssey Extraction: Crewmember game",
    1060:	"Crash Site	Odyssey Extraction: Captain game",
    1070:	"Crash Site	Odyssey Extraction: Onslaught game",
    1200:	"Nexus Blitz - Nexus Blitz game"
}


class LeagueCog(Cog):
    """
    A cog for accessing the League of Legends API.
    """
    def __init__(self, bot):
        # Save our bot for later use
        self.bot = bot
        # Save the league api key and the current league version
        self.league_key = os.environ["LEAGUE_TOKEN"]
        self.league_ver = json.loads(requests.get(LEAGUE_VERSION).text)[0]
        champions = json.loads(requests.get(CHAMPIONS_URL.format(self.league_ver)).text).get("data")
        champNames = {}
        for champ in champions:
            champNames[champions.get(champ).get("key")] = champions.get(champ).get("id")
        self.champNames = champNames

    async def getSummonerData(self, ctx, region, summoner):
        async with self.bot.session.get(BASE_URL.format(region) + SUMMONER_API.format(summoner, self. league_key)) as resp:
            # If the code is 404
            if(resp.status == 404):
                return
            # If the code is 200
            elif(resp.status == 200):
                return await resp.json()

    async def getSummonerRankedData(self, ctx, region, id):
        async with self.bot.session.get(BASE_URL.format(region) + RANKED_API.format(id, self.league_key)) as resp:
            return await resp.json()

    async def getSummonerMatchHistory(self, ctx, region, accountId, params):
        async with self.bot.session.get(BASE_URL.format(region) + MATCHES_API.format(accountId, self.league_key), params=params) as resp:
            return await resp.json()

    async def getMatchInformation(self, ctx, region, matchId):
        async with self.bot.session.get(BASE_URL.format(region) + MATCH_API.format(matchId, self.league_key)) as resp:
            return await resp.json()

    def getPlayerString(self, ctx, player, lane, role):
        if(player.get("lane") == lane):
            if(player.get("role") == role):
                return "{} - {} ({}/{}/{})\n".format(player.get("summonerName"), self.champNames.get(player.get("champion")),
                                                     player.get("kills"), player.get("deaths"), player.get("assists"))
            else:
                return ""
        else:
            return ""

    def secondsToText(ctx, secs):
        days = secs//86400
        hours = (secs - days*86400)//3600
        minutes = (secs - days*86400 - hours*3600)//60
        seconds = secs - days*86400 - hours*3600 - minutes*60
        result = (("{} days, ".format(days) if days else "") + ("{}:".format(hours) if hours else "")
                  + ("{}".format(minutes) if minutes else "") + (":{} ".format(seconds) if seconds else ""))
        return result

    @commands.command(name='lolprofile', aliases=["lp"])
    async def lolprofile(self, ctx, region, summonerName):
        """
        Generates an embed displaying the specified users LoL Profile.
        """
        # Check if the specified region is correct
        if(region.lower() in REGIONS):
            region = REGIONS.get(region.lower())
        else:
            await ctx.send("Region not found. Use one of the following: \nBR, EUNE, EUW, JP, KR, LAN, LAS, NA, OCE, TR, RU, PBE")
            return
        summoner = summonerName
        # Request summoner data
        data = await self.getSummonerData(self, region, summoner)
        if not data:
            await ctx.send('Summoner not found. If using a multi-word summoner name remember to use quotation marks ""')
            return
        # Create an embed to display summoner data
        embed = discord.Embed(title=data.get("name"))
        embed.set_author(name=("Summoner Level - " + str(data.get("summonerLevel"))))
        embed.set_thumbnail(url=PROFILE_IMAGE_URL.format(self.league_ver, data.get("profileIconId")))
        # Request the summoner ranked data
        summonerId = data.get("id")
        rankData = await self.getSummonerRankedData(self, region, summonerId)
        # Check if ranked data exists, otherwise Unranked
        if rankData:
            rankData = rankData[0]
            embed.add_field(name="Rank", value=("{} {}".format(rankData.get("tier"), rankData.get("rank"))), inline=True)
            embed.add_field(name="Ranked W/L", value=("{}/{}".format(rankData.get("wins"), rankData.get("losses"))), inline=True)
            embed.add_field(name="League Points", value=rankData.get("leaguePoints"), inline=True)
        else:
            embed.add_field(name="Unranked", value="\u200b", inline=True)

        await ctx.send(embed=embed)

    @commands.command(name='lolmatches', aliases=["lm"])
    async def lolmatches(self, ctx, region, summonerName, numberOfMatches="1"):
        # Check if the specified region is correct
        if(region.lower() in REGIONS):
            region = REGIONS.get(region.lower())
        else:
            await ctx.send("Region not found. Use one of the following: \nBR, EUNE, EUW, JP, KR, LAN, LAS, NA, OCE, TR, RU, PBE")
            return
        # Request the summoner data
        summoner = summonerName
        data = await self.getSummonerData(self, region, summoner)
        if not data:
            await ctx.send('Summoner not found. If using a multi-word summoner name remember to use quotation marks ""')
            return
        # Check how many matches the user requested
        if(int(numberOfMatches) > 5):
            await ctx.send("I am only allowed to send you a maximum of 5 matches.")
            return
        elif(int(numberOfMatches) < 1):
            numberOfMatches = str(1)
        accountId = data.get("accountId")
        # Request the match history of the summoner
        params = 'endIndex='+numberOfMatches
        matchHistory = await self.getSummonerMatchHistory(self, region, accountId, params)
        for match in matchHistory.get("matches"):
            matchId = match.get("gameId")
            # Request match information
            matchData = await self.getMatchInformation(self, region, matchId)
            # Grab important match data
            gameMode = MATCHMAKING_QUEUES.get(matchData.get("queueId"))
            gameDuration = matchData.get("gameDuration")
            matchTimeStamp = matchData.get("gameCreation")
            # Grab Participant Data
            matchPlayers = []
            for player in (matchData.get("participants")):
                playerDict = {
                    "champion": str(player.get("championId")),
                    "participantId": player.get("participantId"),
                    "assists": str(player.get("stats").get("assists")),
                    "deaths": str(player.get("stats").get("deaths")),
                    "kills": str(player.get("stats").get("kills")),
                    "team": str(player.get("teamId")),
                    "lane": str(player.get("timeline").get("lane")),
                    "role": str(player.get("timeline").get("role")),
                    "win": player.get("stats").get("win")
                }
                matchPlayers.append(playerDict)
            # Grab summoner names from participantIds
            gameinfo = gameMode
            for player in matchPlayers:
                for participant in matchData.get("participantIdentities"):
                    if(player.get("participantId") == participant.get("participantId")):
                        player["summonerName"] = participant.get("player").get("summonerName")
            # Curren time
            time = self.secondsToText(gameDuration)
            # Split players into teams
            blueTeam = matchPlayers[:5]
            redTeam = matchPlayers[5:]
            # TimeStamp calculation
            currentTime = datetime.datetime.now()
            elapsedDays = currentTime - datetime.datetime.fromtimestamp(matchTimeStamp/1000.0)
            if(elapsedDays.days == 0):
                timeStamp = "today"
            elif(elapsedDays.days == 1):
                timeStamp = "1 day ago"
            else:
                timeStamp = str(elapsedDays.days) + " days ago"
            # Embed creation
            embed = discord.Embed(title=(gameinfo + " ({})".format(timeStamp)), description=("Game duration: " + time), colour=0xEDB24C)
            blueTeamSorted = ""
            blueTeamString = ""
            redTeamSorted = ""
            redTeamString = ""
            counter = 0
            for player in blueTeam:
                if(player.get("lane") == "TOP"):
                    first = self.getPlayerString(self, player, "TOP", "SOLO")
                    counter += 1
                if(player.get("lane") == "JUNGLE"):
                    second = self.getPlayerString(self, player, "JUNGLE", "NONE")
                    counter += 1
                if(player.get("lane") == "MIDDLE"):
                    third = self.getPlayerString(self, player, "MIDDLE", "SOLO")
                    counter += 1
                if(player.get("lane") == "BOTTOM" and player.get("role") == "DUO_CARRY"):
                    fourth = self.getPlayerString(self, player, "BOTTOM", "DUO_CARRY")
                    counter += 1
                if(player.get("lane") == "BOTTOM" and player.get("role") == "DUO_SUPPORT"):
                    fifth = self.getPlayerString(self, player, "BOTTOM", "DUO_SUPPORT")
                    counter += 1
                blueTeamString += "{} - {} ({}/{}/{})\n".format(player.get("summonerName"), self.champNames.get(player.get("champion")),
                                                                player.get("kills"), player.get("deaths"), player.get("assists"))
            blueTeamSorted = blueTeamString
            try:
                if first and second and third and fourth and fifth:
                    blueTeamSorted = "{}{}{}{}{}".format(first, second, third, fourth, fifth)
            except UnboundLocalError:
                print("Old game data format.")
            embed.add_field(name="<:large_blue_circle:593787888861315078> BLUE TEAM <:large_blue_circle:593787888861315078>",
                            value=blueTeamSorted, inline=False)
            counter = 0
            for player in redTeam:
                if(player.get("lane") == "TOP"):
                    first = self.getPlayerString(self, player, "TOP", "SOLO")
                    counter += 1
                if(player.get("lane") == "JUNGLE"):
                    second = self.getPlayerString(self, player, "JUNGLE", "NONE")
                    counter += 1
                if(player.get("lane") == "MIDDLE"):
                    third = self.getPlayerString(self, player, "MIDDLE", "SOLO")
                    counter += 1
                if(player.get("lane") == "BOTTOM" and player.get("role") == "DUO_CARRY"):
                    fourth = self.getPlayerString(self, player, "BOTTOM", "DUO_CARRY")
                    counter += 1
                if(player.get("lane") == "BOTTOM" and player.get("role") == "DUO_SUPPORT"):
                    fifth = self.getPlayerString(self, player, "BOTTOM", "DUO_SUPPORT")
                    counter += 1
                redTeamString += "{} - {} ({}/{}/{})\n".format(player.get("summonerName"), self.champNames.get(player.get("champion")),
                                                               player.get("kills"), player.get("deaths"), player.get("assists"))
            redTeamSorted = redTeamString
            try:
                if first and second and third and fourth and fifth:
                    redTeamSorted = "{}{}{}{}{}".format(first, second, third, fourth, fifth)
            except UnboundLocalError:
                print("Old game data format.")
            embed.add_field(name="<:red_circle:593788287974375455> RED TEAM <:red_circle:593788287974375455>", value=redTeamSorted, inline=False)
            if(blueTeam[0].get("win")):
                embed.set_footer(text="Blue team won! The values in parenthesis represent (Kill/Death/Assist)")
            else:
                embed.set_footer(text="Red team won! The values in parenthesis represent (Kill/Death/Assist)")
            await ctx.send(embed=embed)


def setup(bot):
    """
    Our function called to add the cog to our bot.
    """
    # Initial check to see if a league of legends api token exists in our enviroment
    if "LEAGUE_TOKEN" in os.environ:
        bot.add_cog(LeagueCog(bot))
    else:
        print("No league api key available")
