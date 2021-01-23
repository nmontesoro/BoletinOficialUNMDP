"""Módulo para twittear la información del BO de la UNMDP
"""

import tweepy
import json
import bo_unmdp
import sys
from time import sleep

# Cargo los parámetros de la app desde un archivo params.json
with open("params.json", "rt") as fp:
    app_parameters = json.loads(fp.read())
    fp.close()

last_id = int(app_parameters["last_id"])

bo_api = bo_unmdp.BOUnmdpApi()
latest_id = bo_api.ObtieneIdBoletin()

if last_id == latest_id:
    print("No hay nuevos boletines.")

if last_id < latest_id:
    # Hay un boletín nuevo
    auth = tweepy.OAuthHandler(
        app_parameters["api_key"], app_parameters["api_key_secret"])
    auth.set_access_token(app_parameters["access_token"],
                          app_parameters["access_token_secret"])

    twitter_api = tweepy.API(auth)

    data = bo_api.ObtieneDatosBoletin(latest_id)

    bo_parser = bo_unmdp.BOParser()

    threads = bo_parser.GetAllTweets(data)

    try:
        for thread in threads:
            last_status_id = 0
            for tweet in thread:
                while True:
                    try:
                        status = twitter_api.update_status(
                            status=tweet,
                            in_reply_to_status_id=last_status_id,
                            place_id="010d7db066434a8a")
                        last_status_id = status.id
                        # Espero 10s para el próximo tweet en el hilo
                        sleep(10)
                    except tweepy.RateLimitError as rl_err:
                        # Rate limit. Vuelvo a intentar en 30'.
                        print("Hit rate limit. Retrying in 30'.")
                        sleep(1800)
                        continue
                    break
            # Espero 50s entre cada hilo
            sleep(50)

    except bo_unmdp.RequestError as req_err:
        print("Error {}: {}".format(req_err.status_code,
                                    req_err.explanation), file=sys.stderr)
    except tweepy.TweepError as tweep_err:
        print(tweep_err.reason, file=sys.stderr)
    except Exception as err: # pylint: disable=broad-except
        print(err.args, file=sys.stderr)

    app_parameters["last_id"] = latest_id
    with open("params.json", "wt") as fp:
        fp.write(json.dumps(app_parameters))
        fp.close()
