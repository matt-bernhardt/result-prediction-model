# This is to work out how to initialize a variable once and then reset to
# that state repeatedly.
import database
from log import Log


def dataInit():
    return 'bar'


def simulateGame(log, game, season):
    log.message('  Game')
    season += 'baz'
    return season


def simulateSeason(log, gamelist, season):
    # Initialize starting data
    this = season

    # For each event, do X
    for event in enumerate(gamelist):
        this = simulateGame(log, event, this)

    log.message('    Simulate: _' + str(this) + '_')
    log.message('')


if __name__ == "__main__":
    # Log
    log = Log('logs/test_init.log')

    # Database
    database.connect()

    # Initial variable condition
    initial = dataInit()
    log.message('Initial setup:')
    log.message('_' + str(initial) + '_')
    log.message('')

    # Get list of games
    schedule = ['a', 'b', 'c', 'd']

    # Simulate all seasons
    for i in range(10):
        log.message('Cycle ' + str(i))
        simulateSeason(log, schedule, initial)

    # Shut down
    database.disconnect()
    log.end()
