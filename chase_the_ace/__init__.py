''' Chase the Ace '''

import logging
from eventmanager import Evt

logger = logging.getLogger(__name__)

class ChaseTheAce():
    def __init__(self, rhapi):
        self._rhapi = rhapi

    def laps_save(self, args):
        if not args['race_id']:
            return 

        race = self._rhapi.db.race_by_id(args['race_id'])
        race_class = race.class_id
        class_heats = self._rhapi.db.heats_by_class(race_class)

        # Run only if last heat in class
        if class_heats and class_heats[-1].id == race.heat_id:
            # heat = self._rhapi.heat_by_id(race.heat_id)
            races = self._rhapi.db.races_by_heat(race.heat_id)

            winners = {}

            for race in races:
                race_result = self._rhapi.db.race_results(race)

                if race_result:
                    leaderboard = race_result[race_result['meta']['primary_leaderboard']]
                    winner = leaderboard[0]['pilot_id']
                    if winner in winners:
                        winners[winner] += 1
                    else:
                        winners[winner] = 1
                else:
                    logger.warning("Failed building ranking, race result not available")
                    return

            for pilot_id, wins in winners.items():
                if wins > 1:
                    # win
                    pilot = self._rhapi.db.pilot_by_id(pilot_id)
                    self._rhapi.ui.message_alert(self._rhapi.__('Chase the Ace Winner: {}').format(pilot.display_callsign))
                    break
            else:
                # no winners
                wins_text = ""
                for pilot_id in winners:
                    pilot = self._rhapi.db.pilot_by_id(pilot_id)
                    if wins_text:
                        wins_text += ', '
                    wins_text += pilot.display_callsign
                if not wins_text:
                    wins_text = self._rhapi.__('None')

                self._rhapi.ui.message_notify(self._rhapi.__('Wins: {}').format(wins_text))


def initialize(rhapi):
    cta = ChaseTheAce(rhapi)
    rhapi.events.on(Evt.LAPS_SAVE, cta.laps_save)

