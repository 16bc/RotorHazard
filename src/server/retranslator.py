from json_endpoints import AlchemyEncoder
import time
import requests
import json
import gevent


def data_generator(RHData, Results, RACE, getCurrentProfile):
    if RACE.cacheStatus == Results.CacheStatus.VALID:
        results = RACE.results
    else:
        results = Results.calc_leaderboard(RHData, current_race=RACE, current_profile=getCurrentProfile())
        RACE.results = results
        RACE.cacheStatus = Results.CacheStatus.VALID
    payload = {
        "raw_laps": RACE.node_laps,
        "leaderboard": results
    }
    return {"race": payload}


def race_current_retranslator(RHData, Results, RACE, getCurrentProfile, logger):
    header = {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}
    period = 10
    while True:
        t0 = time.time()
        try:
            addr = RHData.get_option('retranslation_server')
            if not addr:
                gevent.sleep(10)
                continue
            period = float(RHData.get_option('retranslation_period', 10))
            struct_data = data_generator(RHData, Results, RACE, getCurrentProfile)
            resp = requests.post(addr, data=json.dumps(struct_data, cls=AlchemyEncoder),
                                    headers=header,
                                    timeout=period)
            # logger.info("Retranslate: " + str(resp.text))

        except Exception as e:
            logger.error("Retranslation error: " + str(e))
        dt = time.time() - t0
        gevent.sleep(period - dt)
