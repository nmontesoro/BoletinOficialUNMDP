"""Módulo para twittear la información del BO de la UNMDP
"""

import tweepy
import json
import bo_unmdp
import sys
import getopt
import logging
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
    logging.debug("Parámetros leídos desde params.json.")
    return parameters


def write_global_params():
    """Guarda los parámetros en params.json.
    """
    with open("params.json", "wt") as fp:
        fp.write(json.dumps(global_params))
        fp.close()
    logging.debug("Parámetros guardados en params.json.")


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
    logging.debug("Objeto tweepy.API creado.")
    return api


def tweet_threads(thread_list: list,
                  tw_api: tweepy.API,
                  rate_limit_wait: int = 1800,
                  dry_run: bool = False,
                  place_id: str = "010d7db066434a8a"):
    """Twittea todos los hilos (threads) en la lista.

    Si llega a haber rate limit, espera el tiempo especificado antes de
    continuar.

    Args:
        threads: lista con los hilos a twittear.
        twitter_api: objeto tweepy.API ya instanciado y listo para
          utilizar.
        rate_limit_wait: entero que indica cuánto tiempo esperar si se
          llega a rate limit (en segundos) (default: 1800 s = 30 min)
        dry_run: indica si twittear o mostrar en pantalla (default:
          False)
        place_id: str que identifica la ubicación desde donde se twittea
          (default: "010d7db066434a8a" - Mar del Plata, AR)
    """
    for thread in thread_list:
        last_status_id = 0
        for tweet in thread:
            while True:
                try:
                    if not dry_run:
                        status = tw_api.update_status(
                            status=tweet,
                            in_reply_to_status_id=last_status_id,
                            place_id=place_id)
                        last_status_id = status.id
                        # Espero 10s para el próximo tweet en el hilo
                        sleep(10)
                    else:
                        print(tweet, "\n--------------------")
                except tweepy.RateLimitError:
                    # Rate limit. Vuelvo a intentar en 30'.
                    message = "Rate limit. Reintentando en {} s.".format(
                        rate_limit_wait)
                    logging.warning(message)
                    sleep(rate_limit_wait)
                    continue
                break
        if not dry_run:
            # Espero 50s entre cada hilo
            sleep(50)
        else:
            print("----------------------------------------")


def parse_cmd_line_arguments(argv):
    """Procesa los argumentos dados a través de la línea de comandos.

    Returns:
        dict con parámetros y valores.
    """
    short_options = "hl:d"
    long_options = ["help", "log-level=", "dry-run"]
    # Uso estos parámetros por defecto
    arguments = {"log_level": logging.INFO,
                 "dry_run": False}

    try:
        opts, args = getopt.getopt(argv, short_options, long_options)
    except getopt.GetoptError:
        print("Argumentos no válidos. " +
              "Utilice -h para ver una lista de argumentos disponibles.")
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            with open("help.txt", "rt") as fp:
                print(fp.read())
                fp.close()
            sys.exit(0)
        if opt in ("-l", "--log-level"):
            if arg.upper() == "WARNING":
                arguments["log_level"] = logging.WARNING
            if arg.upper() == "DEBUG":
                arguments["log_level"] = logging.DEBUG
        if opt in ("-d", "--dry-run"):
            arguments["dry_run"] = True

    return arguments


cmd_args = parse_cmd_line_arguments(sys.argv[1:])
logging.basicConfig(filename="tweet.log",
                    level=cmd_args["log_level"],
                    format="%(asctime)s - %(levelname)s: %(message)s")

logging.info("----- Nueva ejecución -----")
logging.info("Parámetros: %s", " ".join(sys.argv[1:]))

global_params = read_global_params()
last_id = int(global_params["last_id"])
bo_api = bo_unmdp.BOUnmdpApi()
latest_id = bo_api.ObtieneIdBoletin()


if last_id == latest_id:
    logging.info("No hay nuevos boletines.")
elif last_id < latest_id:
    logging.info("Se encontró un boletín (id=%s)", latest_id)
    twitter_api = instantiate_twitter_api(global_params)

    raw_data = bo_api.ObtieneDatosBoletin(latest_id)

    bo_parser = bo_unmdp.BOParser()

    threads = bo_parser.GetAllTweets(raw_data)

    try:
        tweet_threads(threads, twitter_api, dry_run=cmd_args["dry_run"])
    except tweepy.TweepError as tweep_err:
        logging.exception(tweep_err.reason)
    except Exception as err:  # pylint: disable=broad-except
        logging.exception(err.msg)

if not cmd_args["dry_run"]:
    global_params["last_id"] = latest_id
    write_global_params()

logging.info("La aplicación se ejecutó correctamente.")
