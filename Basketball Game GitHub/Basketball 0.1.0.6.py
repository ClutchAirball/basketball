'''Currently, this program simulates a single game of basketball and produces a box score for the game.
The players who participate in the game have generated names (from an extensive list), heights, armspans, and skills.

It is a work in progress to hopefully be a basketball management game, so a lot of the code reflects that.
For example, it currently generates sixty players and populates nine teams and a pool of 'free agents' when it runs, not just
the two teams and ten players participating in the game.

TO-DO:
- tendencies aren't used (enough) yet.
- tendencies are currently independent of skills; they shouldn't be
- skills are currently independent of height/position; they shouldn't be
- the likelihood of a player making a steal is currently based on their skill, not at all their armspan
- no blocked shots yet
- no fouls yet
- turnovers shouldn't necessarily come from a steal
- overall, better simulation of each possession; I want to simulate touches individually, not just possessions
- concept of stamina. This relates to...
- SUBSTITUTIONS! Currently, five players from each team play the whole game
    - remember, the skills and tendencies cdf's should be re-calculated each time there is a substitution
- concept of time, not just possessions
    - simulate the length of a possession
    - possibility for 24 second violations
    - concept of quarters! (Buzzer beaters?)
- all of my game functions add game_stats to an index of [0] ... this won't work once I simulate multiple games.
- adventurous: pick and rolls? Plays? Probably not, at least not for a while
These TO-DOs relate to the simulation of games. Once I've sorted that out, I will work on the management aspect.'''






from tkinter import *
import math
import statistics
import random
import json
import os
import time
import bisect

#The space between columns in a box score
boxscore_space = 5

#The minimum and maximum rating for skills
minrating = 10
maxrating = 99

        
#Five standard basketball positions, stored in a list
pos = ["PG", "SG", "SF", "PF", "C"]

#Define what the skills and tendencies are
skills = ["3pt","mid","pass","playm","hand","post","fin","dunk","perd","posd","speed","jump","stre","orb","drb"]
tendencies = ["3pt","mid","pass","dribble","drive","post","layup","dunk","foul","stl","blk"]

#Define what the counting stats are
stats = ["pts","orb","drb","reb","ast","stl","blk","2pm","2pa","3pm","3pa","ftm","fta","tov","pf","pos","min"]

#Define what the printed stats are
pstats = ["min","pts","reb","ast","stl","blk","tov","pf","fgm","fga","fg%","3pm","3pa","3p%","ftm","fta","ft%","orb","drb","+/-","prf"]

#The average height and standard deviation in cm
#Player heights will be determined with a normal distribution
avg_height = 195
height_sd = 8

'''Rates'''
tov_rate = 0.13



'''
             ######################################        CLASSES       ######################################
'''

class Position:
    ''' This class defines the five basketball positions and also determines what position
    a given player should play'''
    
    #Constructor
    def __init__(self, player):

        #Count a 'score' for how well the player suits a given position. Initialise the count to 0
        #In the end, the highest score is what position the player should play.
        #For example, if the highest score is at index 1, the player should be an SG
        self.count = [0 for i in range(5)]
        
        self.position = ""
        self.second_position = ""

        #Diff is the difference between a player's rating in a given skill relative
        #to their average rating
        diff = {}
        for i in skills:
            diff[i] = player.skills[i] - player.avg

        #Update count with the weights for each position
        ht = player.skills["ht"]
        Position.tally(self,15-((ht-22)/15)**2,15-((ht-45)/10)**2,15-((ht-65)/10)**2,15-((ht-75)/10)**2,15-((ht-90)/10)**2)
            
##        if diff["3pt"] > diff["drb"]:
##            Position.tally(self,3,4,2,1,0)
##        else:
##            Position.tally(self,1,0,1,2,4)

        #Using the final count, choose a position for the player
        self.position = Position.choose(self)
        self.second_position = Position.choose_second(self)
        
    def choose( self ):
        '''Finds which position has the greatest count, and returns that position'''
        
        currentmax = self.count[0]
        currentpos = 0

        #Goes through each position one-by-one to determine which has the greatest count
        for i in range(5):
            if self.count[i] > currentmax:
                currentmax = self.count[i]
                currentpos = i
                
        return pos[currentpos]

    def choose_second( self ):
        '''Finds which position has the second-greatest count, and returns that position'''
        currentmax = self.count[0]
        currentpos = 0
        currentsecond = self.count[1]
        currentsecondpos = 1

        #Goes through each position one-by-one to determine which has the second-greatest count
        #We still keep track of which count has the maximum number, otherwise we can't know which is second-greatest
        for i in range(5):
            
            #If there is a new maximum, update current and secondary
            if self.count[i] > currentmax:

                #The previous maximum must be assigned as the secondary position before we update the maximum
                currentsecond = currentmax
                currentsecondpos = currentpos

                #Update the maximum
                currentmax = self.count[i]
                currentpos = i

            #If there is a position with a count greater than the secondary, but not the maximum (AND isn't the maximum),
            #update just the secondary
            elif self.count[i] > currentsecond and i != currentpos:
                currentsecond = self.count[i]
                currentsecondpos = i
        if currentsecond * 1.1 >= currentmax:
            return pos[currentsecondpos]
        else:
            return ""

    def tally( self, PG, SG, SF, PF, C ):
        '''Updates the count for each position, using a given weight for each position.'''
        self.count[0] += PG
        self.count[1] += SG
        self.count[2] += SF
        self.count[3] += PF
        self.count[4] += C
         
    def __str__(self):
        return self.position

class Player:
    '''This class defines all of the attributes of a player'''
    
    def __init__ (self):

        #Give each player a unique ID
        self.id = len(players)

        #Generate a name
        self.forename = gen_name(england_first,0.005)
        self.surname = gen_name(england_last)

        #Give our player a height, 'listed height', armspan, and standing reach
        #Height uses our predefined average and standard deviation
        self.height = round(random.normalvariate(avg_height, height_sd),1)
        #NBA average "ape index" is 1.06, with a minimum of roughly 1.0 and a maximum of roughly 1.12
        self.armspan = round(random.normalvariate(self.height*1.06, (self.height*0.06)/3),1)
        #Standing reach in the NBA has an average of (height+armspan)/1.5477.
        #The divisor of 1.5477 has a sd of 0.02251, due to some of players' heights being above their shoulders.
        self.reach = round((self.height+self.armspan)/random.normalvariate(1.5477,0.02251),1)
        #Listed height in basketball is the height in shoes, usually rounded up. It's imprecise, so I put some randomness in here.
        self.l_height = Feet.metricround(self.height+((random.random()*3.7)+1.27),0)

        #Generate empty dictionaries for the player's skills and tendencies
        self.skills = {}
        self.tendencies = {}
        #For each attribute, generate random number between the minimum and maximum rating
        #The constants 'skills' and 'tendencies' are defined at the beginning of the code.
        for i in skills:
            self.skills[i] = random.randint(minrating,maxrating)
        for i in tendencies:
            self.tendencies[i] = random.randint(minrating,maxrating)
        
        #A player's 'height' (actually based on standing reach) will be one of our strongest indicators of position.
        self.skills["ht"] = int((((self.reach - ((avg_height*2.06)/1.5477 - 4*height_sd)) / (8 * height_sd)))*100)
        
        #If ht is outside the range 0-100, set ht to 0 or 100
        if self.skills["ht"] < 0:
            self.skills["ht"] = 0
        elif self.skills["ht"] > 100:
            self.skills["ht"] = 100

        #Give each player an average value of their ratings
        self.avg = int(average(self.skills)+0.5)
        
        #Give each player a random pot that is greater than their avg
        self.pot = math.ceil( (random.random() * random.random() * (maxrating-self.avg) ) + self.avg )

        #Create an empty list that will contain the players' game stats
        self.game_stats = []

        #Determine the position of the player
        self.pos = Position(self)

        #Assign the player to first available team with an open spot
        validteam = False
        i = 1
        while validteam == False:
            #If there are less than 5 players on the team, assign the player
            if len(teams[i].players) < 5:
                teams[i].addplayer(self)
                self.team = i
                validteam = True
            elif i == len(teams)-1:
                teams[0].addplayer(self)
                self.team = 0
                validteam = True
            else:
                i += 1
        
    def __str__ (self):
        '''the string of a player returns their full name'''
        return self.forename + " " + self.surname
    
    def print(self,info="vitals"):
        '''returns the name, position, physical attributes, and overall ratings of a player'''
        if info == "vitals":
            return str(self.pos)+" "+str(self.pos.second_position)+"\t"+str(self)[0:15]+"\t"+str(Feet.metricround(self.height,1))+", "+str(Feet.metricround(self.armspan,1))+", "+str(Feet.metricround(self.reach,1))+", "+str(self.avg)+", "+str(self.pot)

class Team:
    '''This class defines the attributes of a team'''
    
    def __init__ (self, city, name="", short="", abbrev=""):
        '''Initialises the team
        city    the location of the team (e.g. Leicester, Madrid)
        name    the full of the team (e.g. Leicester Riders, Real Madrid Baloncesto)
        short   the short name of the team (e.g. Riders, Real Madrid)
        abbrev  the abbreviation of the team (e.g. LEI, RMB)'''
        self.city = city

        #If no full name given, make it the name of the city
        if name == "":
            self.name = city
        else:
            self.name = name

        #If no short name is given, make it the name of the city
        if short == "":
            self.short = city

        #If no abbreviation is given, make it the first three letters of the city, uppercase
        if abbrev == "":
            self.abbrev = self.city[0:3].upper()
        else:
            #The maximum length of the abbreviation is four letters
            self.abbrev = abbrev[0:4].upper()

        #The roster starts off as empty
        self.players = []

    def addplayer(self,player):
        '''Adds a player to the roster'''
        self.players.append(player)

    def printplayers(self):
        '''Prints the players on the team'''
        for i in range (len(self.players)):
            print(self.players[i])
    
    def __str__ (self):
        '''the string of the team returns the full name of the team'''
        if self.name != self.city:
            return self.name
        else:
            return self.city


class Feet:
    '''This class defines how to represent length in feet and inches'''
    
    def __init__ (self, feet, inches):
        '''Stores feet and inches'''
        
        #Feet must be an integer. Include extra inches over 12
        self.feet = int(feet + (inches // 12))
        #Inches can be stored up to three decimal places
        self.inches = round(inches % 12,3)
        
    def metric (length):
        '''Converts a length from cm to feet and inches.'''
        return Feet(0,length/2.54)
    
    def metricround(length,decimal):
        '''Converts a length from cm to feet an inches, and rounds
        to the given number of decimal places.'''
        
        if decimal == 0:
            return Feet(0,int(length/2.54))
        else:
            return Feet(0,round(length/2.54,decimal))
        
    def __str__ (self):
        '''The string returns the standard way of representing feet and inches.
        6ft 7in would be represented as 6'7".'''
        return str(self.feet) + "'" + str(self.inches) + '"'


class player_stats_game():
    '''This class keeps track of a player's stats from a single game.'''
    
    def __init__ (self):
        '''Starts by setting each stat to zero'''

        #Create an empty dictionary
        self.stats = {}

        #For each statistical category, set the value to zero
        #The constant 'stats' is defined at the beginning of the code
        for i in stats:
            self.stats[i] = 0
            
    def add (self, stat):
        '''This function increments the given stat for the player.
        If another stat is dependent on the incremented stat, increase
        the dependent stat as needed (i.e. points are dependent on field
        goals made and total rebounds are dependent on offensive rebounds
        and defensive rebounds)'''
        
        self.stats[stat] += 1
        if stat == "2pm":
            self.stats["pts"] += 2
        elif stat == "3pm":
            self.stats["pts"] += 3
        elif stat == "ftm":
            self.stats["pts"] += 1
        elif stat == "orb" or stat == "drb":
            self.stats["reb"] +=1

    def __str__ (self):
        '''The string of a player's box score stats returns the row of that
        player's stats in the box score, minus their identifying name.
        To actually print a box score for a game, see  the function
        print_game_stats.'''
        string = ""
        for i in stats:
            string += str(self.stats[i])
            string += " " * (boxscore_space-len(str(self.stats[i])))
        return string







'''
             ######################################         FUNCTIONS        ######################################
'''


def game_old(teams):
    possessions = 100
    score1 = 0
    score2 = 0

    pdf = {}
    cdf = {}
    
    for j in 0,1:
        for i in range(len(teams[j].players)):
            teams[j].players[i].game_stats.append(player_stats_game())
            
        pdf[j] = {}
        cdf[j] = {}
        for i in skills:
            pdf[j][i] = []
            for x in range(len(teams[j].players)):
                pdf[j][i].append(teams[j].players[x].skills[i])
            cdf[j][i] = get_cdf(pdf[j][i])

    tpdf = {}
    tcdf = {}
    
    for j in 0,1:
        for i in range(len(teams[j].players)):
            teams[j].players[i].game_stats.append(player_stats_game())
            
        tpdf[j] = {}
        tcdf[j] = {}
        for i in skills:
            tpdf[j][i] = []
            for x in range(len(teams[j].players)):
                tpdf[j][i].append(teams[j].players[x].skills[i])
            tcdf[j][i] = get_cdf(tpdf[j][i])



    score1 = play_game (score1, teams[0], teams[1], possessions, cdf)
    score2 = play_game (score2, teams[1], teams[0], possessions, cdf)

    print_game_stats(teams)
    
    print(score1, "-", score2)





    

def game(teams):
    score = [0,0]
    lineup = {}
    tallest = []
    tallestplayer = []
    for i in 0,1:
        for j in range(len(teams[i].players)):
            teams[i].players[j].game_stats.append(player_stats_game())
        lineup[i] = starting5(teams[i])
        tallest.append(lineup[i][0].reach)
        tallestplayer.append(lineup[i][0])
        for j in range(5):
            if tallest[i] < lineup[i][j].reach:
                tallest[i] = lineup[i][j].reach
                tallestplayer[i] = lineup[i][j]

    pdf = {}
    cdf = {}

    for j in 0,1:
        pdf[j] = {}
        cdf[j] = {}
        for i in skills:
            pdf[j][i] = []
            for x in range(5):
                pdf[j][i].append(lineup[j][x].skills[i])
            cdf[j][i] = get_cdf(pdf[j][i])

    tpdf = {}
    tcdf = {}
    
    for j in 0,1:
        tpdf[j] = {}
        tcdf[j] = {}
        for i in tendencies:
            tpdf[j][i] = []
            for x in range(5):
                tpdf[j][i].append(lineup[j][x].tendencies[i])
            tcdf[j][i] = get_cdf(tpdf[j][i])
            
    who_has_ball = jumpball(tallestplayer[0],tallestplayer[1])


    
    for i in range(160):
        who_has_ball = possession(who_has_ball,teams,cdf,tcdf,score)

    print_game_stats(teams)

    print(score[0],"-",score[1])





        
        

def jumpball(player0,player1):
    player1_chance = player1.reach+(player1.skills["jump"]/2)+30
    player0_chance = player0.reach+(player0.skills["jump"]/2)+30
    random_range = player1_chance + player0_chance
    if random.random()*random_range <= player0_chance:
        who_has_ball = 0
    else:
        who_has_ball = 1
    return who_has_ball
        

def starting5(team):
    playerlist = []
    for i in range(len(team.players)):
        playerlist.append(team.players[i])
        playerlist.sort(key=lambda Player: Player.avg,reverse=True)
    return playerlist[0:5]

def print_game_stats(teams):
    
    length = 1
    for j in 0,1:
        for i in range(len(teams[j].players)):
            if len(teams[j].players[i].surname) > length:
                length = len(teams[j].players[i].surname)
    header = " " * (length + 2)
    
    for i in stats:
        header += i
        header += " " * (boxscore_space-len(i))

    for j in 0,1:
        print(teams[j])
        print(header)
        totalstring = ""
        total = {}
        for i in stats:
            total[i] = 0
        for i in range(len(teams[j].players)):
            print(teams[j].players[i].surname, " " * (length - len(teams[j].players[i].surname)), teams[j].players[i].game_stats[0])
            for x in stats:
                total[x] += teams[j].players[i].game_stats[0].stats[x]
        for x in stats:
            totalstring += str(total[x])
            totalstring += " " * (boxscore_space-len(str(total[x])))
        print("TOTAL", " " * (length - 5), totalstring)
        print("")
    

def play_game (score, team, other_team, possessions,cdf):
    for i in range(possessions):
        shooter = team.players[random.randint(0,4)]
        shottype = random.randint(2,3)
        if shottype == 3:
            score = attempt_3FG(score,team,other_team,shooter,cdf[0],cdf[1])
        else:
            score = attempt_mid(score,team,other_team,shooter,cdf[0],cdf[1])
    return score


def possession (pos,teams,cdf,tcdf,score):
    if pos == 0:
        other = 1
    else:
        other = 0
        
    if random.random() < tov_rate:
        turnoverer = bisect.bisect(cdf[pos]["hand"], random.random()*cdf[pos]["hand"][-1])
        teams[pos].players[turnoverer].game_stats[0].add("tov")
        teams[pos].players[turnoverer].game_stats[0].add("pos")

        stealer = bisect.bisect(tcdf[other]["stl"], random.random()*tcdf[other]["stl"][-1])
        teams[other].players[stealer].game_stats[0].add("stl")
        return other
    else:
        shottype = random.random()
        if shottype < 0.6:
            shooter = teams[pos].players[bisect.bisect(tcdf[pos]["mid"],random.random()*tcdf[pos]["mid"][-1])]
            results=[0,0]
            results=attempt_mid(score[pos],teams[pos],teams[other],shooter,cdf[pos],cdf[other],pos,other)
            score[pos] = results[0]
        else:
            shooter = teams[pos].players[bisect.bisect(cdf[pos]["3pt"],random.random()*cdf[pos]["3pt"][-1])]
            results=[0,0]
            results=attempt_3FG(score[pos],teams[pos],teams[other],shooter,cdf[pos],cdf[other],pos,other)
            score[pos] = results[0]
        return results[1]
        
        
    
def get_cdf (values):
    '''Creates a cumulative distribution function for a given probability density function'''

    #Initialise the cdf to the pdf
    cdf = values

    #Make each value equal to itself plus the previous value. This has the effect of creating a cdf
    #The loop starts as 1 because the value at index 0 is already correct (the first value of a pdf = the first value of its cdf)
    #For each successive value, adding the current pdf to the previous value in the cdf produces the cdf
    #(e.g.: [4,6,5,4,3,2,7] goes to [4,10,15,19,22,24,31]
    
    for i in range(1,len(values)):
        cdf[i] = cdf[i-1] + cdf[i]
    return cdf



def choose_from_skill (players, skill):
    pdf = []
    for i in range(len(players)):
        pdf.append(players[i].skills[skill])
    cdf = get_cdf(pdf)
    chosenplayer = players[bisect.bisect(cdf,random.random()*cdf[-1])]
    return chosenplayer



        
def attempt_3FG(score,team,other_team,shooter,cdf,cdf2,pos,other):
    '''A given player is attempting a three-pointer. This function determines whether they make the shot.
    If they miss, it determines which player (and team) secures the rebound'''
    
    #Maximum chance of making a three is 50%
    #Generate a random number. If it is lower than the shooter's 3pt rating times 0.005, a made basket is recorded
    if random.random() < shooter.skills["3pt"]*0.005:
        
        #Increase the team's score and the relevant stats
        score += 3
        shooter.game_stats[0].add("3pm")
        shooter.game_stats[0].add("3pa")
        shooter.game_stats[0].add("pos")
        
        #85% of three-pointers are assisted
        if random.random() < 0.85:
            team.players[bisect.bisect(cdf["pass"], random.random()*cdf["pass"][-1])].game_stats[0].add("ast")
        pos = other
    else:
        #If the shooter misses, increase the relevant stats
        shooter.game_stats[0].add("3pa")
        shooter.game_stats[0].add("pos")
        #25% chance of offensive rebounds. Whoever gets the board, generate the relevant stats.
        if random.random() < 0.27:
            team.players[bisect.bisect(cdf["orb"], random.random()*cdf["orb"][-1])].game_stats[0].add("orb")
            pos = pos
        else:
            other_team.players[bisect.bisect(cdf2["drb"], random.random()*cdf2["drb"][-1])].game_stats[0].add("drb")
            pos = other
    return [score,pos]

def attempt_mid(score,team,other_team,shooter,cdf,cdf2,pos,other):
    '''A given player is attempting a mid-range jumpshot. This function determines whether they make the shot.
    If they miss, it determines which player (and team) secures the rebound'''
    
    #Maximum chance of making a mid is 60%
    #Generate a random number. If it is lower than the shooter's mid rating times 0.006, a made basket is recorded
    if random.random() < shooter.skills["3pt"]*0.006:
        score += 2
        shooter.game_stats[0].add("2pm")
        shooter.game_stats[0].add("2pa")
        shooter.game_stats[0].add("pos")
        if random.random() < 0.51:
            team.players[bisect.bisect(cdf["pass"], random.random()*cdf["pass"][-1])].game_stats[0].add("ast")
        pos = other
    else:
        shooter.game_stats[0].add("2pa")
        shooter.game_stats[0].add("pos")
        if random.random() < 0.27:
            team.players[bisect.bisect(cdf["orb"], random.random()*cdf["orb"][-1])].game_stats[0].add("orb")
            pos = pos
        else:
            other_team.players[bisect.bisect(cdf2["drb"], random.random()*cdf2["drb"][-1])].game_stats[0].add("drb")
            pos = other
    return [score, pos]



    
        

def frequency_histogram(values):
    '''draws a histogram of the values it is given'''

    #Creates an empty table
    table = {}

    #Go through each item in the list and add it to the histogram
    for i in values:

        #Increase the value for the item's key by one
        #If it is the first instance of that item, create a new key for it, set the value to zero, and increment it by one
        table[i] = table.get(i,0) + 1

    #Sort the table and print it
    for i in sorted(table):
        print(i,'x'*(table[i]))
        

def ratings_histogram (players, attribute):
    '''generates a list of the ratings for many players
    players    the list of players
    attribute  the attribute for which to draw a histogram'''

    #Create a list of the particular attribute we wish to create a histogram of
    rating_list = []
    for i in range(len(players)):
        rating_list.append(int(players[i].attribute))

    #Use the histogram function to print the ratings histogram
    frequency_histogram(rating_list)
    

def average(values):
    '''finds the mean of a given list of values'''
    
    total = 0

    #Find the sum of all the values
    for i in values:
        total = total + values[i]

    #Divide by the number of values
    average = total / len(values)
    
    return average


def gen_name(nameset,prob=0.025):
    '''Chooses a name from a given nameset, with a probability (prob) of a double-barrelled name being generated.
    cprob is automatically set to 2.5%

    The names in the nameset should be ordered according to a cumulative distribution function (cdf).
    The get_names function should have already sorted out the cdf.'''

    #Generate a random number between 0 and the total cumulative frequency of names
    randno = random.random()*nameset["cdf"][-1]

     #Choose 
    name_num = bisect.bisect(nameset["cdf"],randno)

    #Small chance of a double-barrelled name
    compound = random.random()
    
    if compound < prob:
        
        name_num2 = name_num
        #Makes sure the two names aren't the same
        while name_num2 == name_num:
            randno2 = random.random()*nameset["cdf"][-1]
            name_num2 = bisect.bisect(nameset["cdf"],randno2)

        #Return the double-barrelled name with a hyphen in between
        return nameset["name"][name_num] + "-" + nameset["name"][name_num2]

    #If no double-barrelled name is generated, return the single name
    else:
        return nameset["name"][name_num]

def get_names(file):
    '''
    Loads a json name file and constructs a cumulative distribution function.
    The name file should contain
        the names as an array that is the key for the value "names"
        the related probability density function of those names as a key for the value "pdf"
    '''
    json_file = open(os.getcwd() + "/Names/" + file)
    data = json.load(json_file)

    #Create a cumulative distribution function based on the probability density function.
    data["cdf"] = data["pdf"]
    for i in range( 1, len(data["cdf"]) ):
        data["cdf"][i] = data["cdf"][i-1]+data["cdf"][i]
    return data


def teams_players_list():
    '''Prints a list of all the teams and their players'''
    for i in range(len(teams)):
        print (teams[i])
        for j in range(len(teams[i].players)):
            print(" ",teams[i].players[j])
        print ("")
        

def all_players_vitals():
    '''Prints the "vital" stats of every player'''
    for i in range(len(players)):
        print(players[i].print("vitals"))
                       
england_first = get_names("England_First.json")
england_last = get_names("England_Last.json")

teams = [Team("Free Agents"),
         Team("Edinburgh"),
         Team("Aberdeen", "Aberdeen Energy", "Energy"),
         Team("Glasgow"),
         Team("Inverness"),
         Team("Dundee"),
         Team("Perth"),
         Team("Ayr"),
         Team("Dunfermline"),
         Team("Paisley")]

players = []
for i in range(60):
    players.append(Player())

game([teams[1],teams[2]])












