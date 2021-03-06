import database
from log import Log
import numpy as np


# This prediction model is deprecrated and should no longer be run. It is
# included here for historical reasons only.
#
# This model is extremely naive, simulating each game result based only on
# which team is playing at home (lines 140-149).
#
# Before running the model, several things must be checked and updated
# manually:
# 1. If needed, update the SQL statement on lines 27-34 to retrieve the
#    current season's games.
# 2. The current points totals for each team must be updated on lines 49-70.
# 3. Also, for seasons other than 2017, the list of teams itself should be
#    updated - using their three-letter abbreviations (i.e. 'CLB' for
#    Columbus)
# 4. The names of the log and output files (lines 135 and 157, respectively)
#    should be updated, unless you are comfortable overwriting the last run.
#
# (I wonder why this version is deprecated...)

def loadGames():
    # This should be passed from outside, so we just get records once
    sql = ("SELECT g.ID, h.team3ltr AS Home, a.team3ltr AS Away "
           "FROM tbl_games g "
           "INNER JOIN tbl_teams h on g.HTeamID = h.ID "
           "INNER JOIN tbl_teams a on g.ATeamID = a.ID "
           "WHERE YEAR(g.MatchTime) = 2017 "
           "AND g.MatchTypeID = 21 "
           "AND g.MatchTime > NOW() "
           "ORDER BY g.MatchTime ASC")
    log.message(sql)
    rs = database.query(sql, ())

    if (rs.with_rows):
        records = rs.fetchall()

    return records


def modelInit():
    # Teams
    # Points
    # Ideally this will calculate points from stored records
    points = {}
    points['CLB'] = 22   # Columbus
    points['DC'] = 15   # DC
    points['CHI'] = 25   # Chicago
    points['COL'] = 13   # Colorado
    points['NE'] = 20   # New England
    points['DAL'] = 23   # Dallas
    points['SJ'] = 19   # San Jose
    points['KC'] = 25   # Kansas City
    points['LA'] = 18   # Los Angeles
    points['NY'] = 20   # New York
    points['POR'] = 21   # Portland
    points['SEA'] = 19   # Seattle
    points['VAN'] = 19   # Vancouver
    points['MON'] = 16   # Montreal
    points['RSL'] = 14   # Salt Lake
    points['HOU'] = 23   # Houston
    points['TOR'] = 29   # Toronto
    points['PHI'] = 16   # Philadelphia
    points['ORL'] = 24   # Orlando
    points['MIN'] = 14   # Minnesota
    points['NYC'] = 24   # New York City
    points['ATL'] = 18   # Atlanta
    return points


def outputClose(dest):
    dest.close()


def outputInit(filename, array):
    # Create output file
    dest = open(filename, 'w')
    # Write header row of array keys
    for key in sorted(array.keys()):
        dest.write(str(key) + ',')
    dest.write('\n')
    # Return
    return dest


def outputPoints(dest, array):
    # This writes out a single row of the model output
    for key in sorted(array.keys()):
        dest.write(str(array[key]) + ',')
    dest.write('\n')


def simulateGame(points, homeThreshold, home, drawThreshold, away, log):
    # Random number
    result = np.random.random(1)[0]

    # Return H/D/A based on random number
    if (result <= homeThreshold):
        # Home win
        points[home] += 3
    elif (result <= drawThreshold):
        # Draw
        points[home] += 1
        points[away] += 1
    else:
        # Away win
        points[away] += 3

    return points


def simulateSeason(gamelist, homeThreshold, drawThreshold, log, output, database):
    log.message('Starting season')

    # Get starting position
    points = modelInit()

    log.message('Points loaded')

    # For each game in the list, simulate the result and calculate points array
    for game in enumerate(gamelist):
        points = simulateGame(points, homeThreshold, game[1][1], drawThreshold, game[1][2], log)

    # After simulating all games
    # Store final points totals for all teams in CSV file for later analysis
    outputPoints(output, points)
    log.message('')


if __name__ == "__main__":
    # Log
    log = Log('logs\model_v1_170605.log')

    # Database
    database.connect()

    # Build odds of result (for now, static)
    log.message('Calculating result odds')
    home = 972.0
    draw = 533.0
    away = 450.0
    homeThreshold = home / (home + draw + away)
    log.message('Home: ' + str(homeThreshold))
    drawThreshold = (home + draw) / (home + draw + away)
    log.message('Draw: ' + str(drawThreshold))
    log.message('')

    # Get starting position
    points = modelInit()

    # Initialize output file
    # This is after the points array init because the first step is to
    # write the array keys as the header row.
    output = outputInit('output\model_v1_170605.csv', points)

    log.message(str(points.keys()))
    log.message(str(points))

    # Get list of games
    schedule = loadGames()

    # Simulate a season
    for i in range(10000):
        log.message('Season ' + str(i))
        simulateSeason(schedule, homeThreshold, drawThreshold, log, output, database)

    # End simulating a season

    # Shut down
    database.disconnect()
    outputClose(output)
    log.end()
