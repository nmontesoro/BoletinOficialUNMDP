"""Módulo para acceder al BO de la UNMDP y utilizar la información.
"""
import requests
import textwrap
import logging
from bs4 import BeautifulSoup


MAIN_URL = "http://digesto.mdp.edu.ar/"


class RequestError(Exception):
    """Cuando el estado del request no es 200 (OK).

    Args:
        status_code: HTTP Status code.
        explanation: Una explicación posible del código.
    """

    def __init__(self, status_code, explanation):
        self.status_code = status_code
        self.explanation = explanation
        super().__init__(explanation)


class BOUnmdpApi:
    """Una clase que permite fácil acceso al Boletín Oficial de la UNMDP.
    """

    def _GetRequest(self, url: str, data: dict = None):
        raise NotImplementedError

    def _PostRequest(self, url: str, data: dict = None):
        response = requests.post(url, data=data)

        if response.status_code != 200:
            raise RequestError(response.status_code, response.reason)

        return response

    def _ParseDatosBoletin(self, data: list) -> list:
        """Limpia el campo Resumen del objeto data para eliminar el CSS.

        Returns:
            El mismo objeto data pasado como parámetro, con el campo
            Resumen alterado.
        """
        for datum in data:
            bs = BeautifulSoup(datum["resumen"], "html.parser")
            datum["resumen"] = bs.get_text()

        logging.debug("Datos del boletín procesados correctamente.")

        return data

    def ObtieneIdBoletin(self) -> int:
        """Devuelve el ID del Boletín Oficial más reciente como int.

        Raises:
            RequestError: si hubo un error al hacer el request.
            Exception: si el servidor no devolvió los datos como se
              esperaba.
        """
        endpoint = "vista/obtiene_id_boletin.php"
        id_boletin = 0

        response = self._PostRequest(MAIN_URL + endpoint)

        js = response.json()

        if "id_boletin" in js:
            id_boletin = int(js["id_boletin"])
        else:
            raise Exception("El servidor no devolvió los datos esperados.")

        logging.debug(
            "El ID del boletín más reciente es {}.".format(id_boletin))

        return id_boletin

    def ObtieneDatosBoletin(self, id_boletin: int) -> list:
        """Devuelve los datos de un Boletín especificado.

        Args:
            id_boletin: El ID del Boletín Oficial cuyos datos se
              pretende extraer.

        Returns:
            Un dict con los datos. Ver la documentación para más info.

        Raises:
            RequestError: si hubo un error al hacer el request.
        """
        endpoint = "vista/obtiene_datos_boletin.php"
        data = {"id_boletin": id_boletin}

        response = self._PostRequest(MAIN_URL + endpoint, data)

        logging.debug(
            "Se obtuvieron los datos del boletín (id={}).".format(id_boletin))

        return self._ParseDatosBoletin(response.json())

    def ObtieneTextos(self, id_norma: int) -> list:
        """Devuelve los datos de una norma según su id.

        Args:
            id_norma: El ID de la norma cuyos datos se pretende extraer.

        Returns:
            Un dict con los datos. Ver la documentación para más info.

        Raises:
            RequestError: si hubo un error al hacer el request.
        """

        endpoint = "vista/obtiene_textos.php"
        data = {"id_norma_modifica": id_norma}

        response = self._PostRequest(MAIN_URL + endpoint, data)

        logging.debug(
            "Se obtuvieron los textos de la norma (id={}).".format(id_norma))

        return response.json()


class BOParser:
    """Clase para procesar la información de la "API" de la UNMDP.
    """

    def GetAllTweets(self, data: list) -> list:
        """Compila la información dada en forma de tweets.

        Returns:
            Lista con tweets.
        """
        endpoint = "vista/ver_norma.php?id_norma="
        tweets = []

        for datum in data:
            content = "{categoria} {numero} - {organo}\n\n{resumen}".format(
                **datum)
            thread = textwrap.wrap(
                text=content, width=280, replace_whitespace=False)

            last_tweet = "Fecha: {fecha_norma} (publicado el {fecha_publicacion})\n".format(
                **datum)
            last_tweet += "Ver " + MAIN_URL + endpoint + datum["id_norma"]

            thread.append(last_tweet)
            tweets.append(thread)

        logging.debug("Listado de tweets generado.")

        return tweets
