import database
from log import Log
import numpy as np


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
    points['CLB'] = 19   # Columbus
    points['DC'] = 14   # DC
    points['CHI'] = 24   # Chicago
    points['COL'] = 10   # Colorado
    points['NE'] = 16   # New England
    points['DAL'] = 20   # Dallas
    points['SJ'] = 19   # San Jose
    points['KC'] = 22   # Kansas City
    points['LA'] = 17   # Los Angeles
    points['NY'] = 20   # New York
    points['POR'] = 18   # Portland
    points['SEA'] = 16   # Seattle
    points['VAN'] = 16   # Vancouver
    points['MON'] = 13   # Montreal
    points['RSL'] = 14   # Salt Lake
    points['HOU'] = 20   # Houston
    points['TOR'] = 29   # Toronto
    points['PHI'] = 16   # Philadelphia
    points['ORL'] = 20   # Orlando
    points['MIN'] = 14   # Minnesota
    points['NYC'] = 20   # New York City
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
    log = Log('logs\model_v1_170529.log')

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
    output = outputInit('output\model_v1_170529.csv', points)

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
