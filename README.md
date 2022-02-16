# Visualizador de estrategias

### Derivatech
#### Desarrollado por Marcos Ortiz-Tirado, contacto: marcos.ortiztirado@gmail.com

Esta aplicación web fue la base sobre la que se creó la interfaz del primer Reto Derivatech36, llevado a cabo durante agosto y semptiembre del año 2021.
Las bases del concurso fueron publicadas en https://derivatech.mx/derivatech360/

![](https://derivatech.mx/derivatech360/assets/images/derivatech360.png)

Para utilizar la aplicación web visita el siguiente enlace: http://motmotm.pythonanywhere.com/

Si lo requiere, utiliza:
* usuario: marcos
* contraseña: derivatech

## Requerimientos

En este proyecto se uitlizaron las librerías `Dash` y `Plotly`para desarrollar la interfaz. Mientras que los datos de los precios de las Acciones y Opciones son obtenidos de Tradier a través de su API.
Se utiliza `Pandas` para el manejo de datos.


## Estrategias

Las estrategias están compuestas por 5 elementos:
* Subyacente: acción en la que está basada la estrategia.
* Precio objetivo: precio del subyacente que condiciona el éxito de la estrategia.
* Dirección: indica si el precio del subyacente deberá de estar por encima o debajo del precio objetivo.
* Fecha de vencimiento: fecha en la que el subyacente deberá de cumplir con la condición establecida por precio objetivo y dirección.
* Rendimiento: campo calculado con base en el mercado y que depende de todos los elementos anteriores.

Una estrategia es "Exitosa" cuando el precio de la acción finaliza arriba o abajo (dependiendo de la Dirección elegida) del Precio objetivo seleccionado en la fecha de vencimiento al cierre del mercado.

Una estrategia "Exitosa" otorga su rendimiento registrado.

Una estrategia "No exitosa" otorga un rendimiento de -100.00%
