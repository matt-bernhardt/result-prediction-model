import database
from log import Log
import numpy as np


# This prediction model is deprecrated and should no longer be run. It is
# included here for historical reasons only.
#
# This model is extremely naive, simulating each game result based only on
# which team is playing at home (lines 137-146).
#
# Before running the model, several things must be checked and updated
# manually:
# 1. If needed, update the SQL statement on lines 26-31 to retrieve the
#    current season's games.
# 2. The current points totals for each team must be updated on lines 46-67.
# 3. Also, for seasons other than 2017, the list of teams itself should be
#    updated - using their ID values (i.e. 11 for Columbus)
# 4. The names of the log and output files (lines 132 and 154, respectively)
#    should be updated, unless you are comfortable overwriting the last run.
#
# (I wonder why this version is deprecated...)

def loadGames():
    # This should be passed from outside, so we just get records once
    sql = ("SELECT ID, HTeamID, ATeamID "
           "FROM tbl_games "
           "WHERE YEAR(MatchTime) = 2017 "
           "AND MatchTypeID = 21 "
           "AND MatchTime > NOW() "
           "ORDER BY MatchTime ASC")
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
    points[11] = 13   # Columbus
    points[12] = 11   # DC
    points[13] = 11   # Chicago
    points[14] = 4   # Colorado
    points[15] = 10   # New England
    points[16] = 15   # Dallas
    points[17] = 12   # San Jose
    points[18] = 15    # Kansas City
    points[19] = 7    # Los Angeles
    points[20] = 16   # New York
    points[42] = 17    # Portland
    points[43] = 10    # Seattle
    points[44] = 10    # Vancouver
    points[45] = 7    # Montreal
    points[340] = 8   # Salt Lake
    points[427] = 13   # Houston
    points[463] = 13   # Toronto
    points[479] = 4   # Philadelphia
    points[506] = 18   # Orlando
    points[521] = 8   # Minnesota
    points[547] = 13  # New York City
    points[599] = 11   # Atlanta
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
    log = Log('logs\model170403.log')

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
    output = outputInit('output\model170403.csv', points)

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
