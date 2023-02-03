# BoletinOficialUNMDP

## English
This is a bot that reads the official bulletin of Universidad Nacional de Mar del Plata and tweets a summary for 
each article, along with a link to the original publication. Check it out at
[@BoletinUnmdp](https://twitter.com/BoletinUnmdp).

## Spanish
Un bot que lee el Boletín Oficial de la Universidad Nacional de Mar del Plata y reproduce el contenido en Twitter.
Se puede ver en funcionamiento siguiendo [@BoletinUnmdp](https://twitter.com/BoletinUnmdp).

## Cómo se utiliza
```tweet.py [opciones]```

### Argumentos posibles
* `-h`, `--help`: Muestra la ayuda.

* `-l:INFO`, `--log-level=INFO`: Establece el nivel de logging (debug, info, warning.)
 Guarda el output en tweet.log.

* `-d`, `--dry-run`: Muestra los tweets en pantalla en vez de enviarlos. Causa que no 
se guarde el id del último boletín procesado (es decir, es útil para cuando se 
quiere visualizar la información antes de que sea twitteada.)

*Importante: es necesario tener un archivo `params.json` donde se
encuentren tanto las claves para la API de Twitter como el ID del último
Boletín Oficial procesado.*

## Archivo `params.json`
Debajo se encuentra la estructura que debería tener el archivo que aloje
los parámetros del programa.

```
{
    "last_id": 0,
    "api_key": "...",
    "api_key_secret": "...",
    "access_token": "...",
    "access_token_secret": "..."
}
```

`last_id` puede ser igual a `0` para la primera vez que se
utilice el programa.

`api_key` y `api_key_secret` corresponden a la aplicación,
mientras que `access_token` y `access_token_secret` al usuario (el
bot). Ver [la documentación de Tweepy](https://docs.tweepy.org/en/latest/auth_tutorial.html) para más información.

Justo antes de que hubiera finalizado la ejecución del programa, se
guarda en este archivo el ID del Boletín Oficial que se procesó.

## Módulo `bo_unmdp`
Toda la información necesaria para la implementación de código que
haga uso de este módulo está en el código fuente, en forma de
comentarios. Sólo se provee aquí más información sobre la estructura de
los objetos devueltos por algunos métodos.
### Clase `BOUnmdpApi`
Observación: los nombres de los métodos son los mismos que el endpoint
al que hacen referencia, pero utilizando las convenciones PEP8.
#### Método `ObtieneDatosBoletin`
Devuelve **una lista de dict**, cada uno con la siguiente estructura:
```
{
    "categoria": "(ordenanza, resolución, etc.)"
    "fecha_carga": "",
    "fecha_norma": "",
    "fecha_publicacion": "",
    "id": "(id del BO al que corresponde)",
    "id_norma": "(id utilizado para esta norma)",
    "nro_boletin": "",
    "numero": "(número de norma),
    "organo": "(Consejo Superior, Rectorado, etc.)",
    "resumen": "",
    "texto_modificado": ""
}
```
Es básicamente lo que devuelve el endpoint `obtiene_datos_boletin`. La
única modificación que se hace es borrar el CSS del campo `resumen`,
para que quede sólo el texto (que después pasa a ser el contenido de los
tweets.)

#### Método `ObtieneTextos`
Devuelve **una lista de dict**, cada uno con la siguiente estructura:
```
{
    "anio_norma": "",
    "aprobada": "",
    "categoria": "(ordenanza, resolución, etc.)",
    "documento": "(nombre del archivo PDF de la norma)",
    "documento_adjunto": "(nombre del archivo PDF del adjunto)",
    "fecha_publicacion": "",
    "id_modificado": "",
    "numero_norma": "",
    "organo": "",
    "resumen": "",
    "texto_modificado": "",
    "texto_original": "",
    "usuario_aprobador": "",
    "usuario_carga": "",
    "usuario_publicador": ""
}
```
En este caso no se modifica ningún campo. `resumen`, `texto_modificado`
y `texto_original` tienen el CSS tal como lo devuelve el endpoint
`obtiene_textos`.

