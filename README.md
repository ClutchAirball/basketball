**This is no longer being updated. For the updated version of the basketball game, see the repo Basketball_Game**








Currently, this program simulates a single game of basketball and produces a box score for the game.
The players who participate in the game have generated names (from an extensive list), heights, armspans, and skills.

The 'Names' folder needs to be a folder in the same directory as the Python file.

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
These TO-DOs relate to the simulation of games. Once I've sorted that out, I will work on the management aspect.
