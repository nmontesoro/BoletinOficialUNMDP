"""Módulo para twittear la información del BO de la UNMDP
"""

import tweepy
import json
import bo_unmdp
import sys
from time import sleep

PLACE_ID = "010d7db066434a8a"  # Mar del Plata, AR


def read_global_params() -> dict:
    """Carga los parámetros necesarios desde un archivo params.json.

    El archivo params.json contiene el ID del último boletín twitteado y
    las claves para utilizar la API de Twitter.
    """
    with open("params.json", "rt") as fp:
        parameters = json.loads(fp.read())
        fp.close()
    return parameters


def write_global_params():
    """Guarda los parámetros en params.json.
    """
    with open("params.json", "wt") as fp:
        fp.write(json.dumps(global_params))
        fp.close()


def instantiate_twitter_api(params: dict):
    """Genero el objeto necesario para utilizar la API de Twitter.

    Args:
        params: dict con las claves necesarias para autenticación.

    Returns:
        Objeto tweepi.API autenticado y listo para utilizar.
    """
    auth = tweepy.OAuthHandler(
        params["api_key"], params["api_key_secret"])

    auth.set_access_token(params["access_token"],
                          params["access_token_secret"])

    api = tweepy.API(auth)
    return api


def tweet_threads(
    thread_list: list, tw_api: tweepy.API, rate_limit_wait: int = 1800):
    """Twittea todos los hilos (threads) en la lista.

    Si llega a haber rate limit, espera el tiempo especificado antes de
    continuar.

    Args:
        threads: lista con los hilos a twittear.
        twitter_api: objeto tweepy.API ya instanciado y listo para
          utilizar.
        rate_limit_wait: entero que indica cuánto tiempo esperar si se
          llega a rate limit (en segundos) (default: 1800 s = 30 min)
    """
    for thread in thread_list:
        last_status_id = 0
        for tweet in thread:
            while True:
                try:
                    status = tw_api.update_status(
                        status=tweet,
                        in_reply_to_status_id=last_status_id,
                        place_id=PLACE_ID)
                    last_status_id = status.id
                    # Espero 10s para el próximo tweet en el hilo
                    sleep(10)
                except tweepy.RateLimitError:
                    # Rate limit. Vuelvo a intentar en 30'.
                    print("Hit rate limit. Retrying in 30'.")
                    sleep(rate_limit_wait)
                    continue
                break
        # Espero 50s entre cada hilo
        sleep(50)


global_params = read_global_params()
last_id = int(global_params["last_id"])
bo_api = bo_unmdp.BOUnmdpApi()
latest_id = bo_api.ObtieneIdBoletin()


if last_id == latest_id:
    print("No hay nuevos boletines.")
elif last_id < latest_id:
    # Hay un boletín nuevo
    twitter_api = instantiate_twitter_api(global_params)

    raw_data = bo_api.ObtieneDatosBoletin(latest_id)

    bo_parser = bo_unmdp.BOParser()

    threads = bo_parser.GetAllTweets(raw_data)

    try:
        tweet_threads(threads, twitter_api)
    except bo_unmdp.RequestError as req_err:
        print("Error {}: {}".format(req_err.status_code,
                                    req_err.explanation), file=sys.stderr)
    except tweepy.TweepError as tweep_err:
        print(tweep_err.reason, file=sys.stderr)
    except Exception as err:  # pylint: disable=broad-except
        print(err.args, file=sys.stderr)

    global_params["last_id"] = latest_id
    write_global_params()
