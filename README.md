# Visualizador de estrategias

### Derivatech
#### Desarrollado por Marcos Ortiz-Tirado, contacto: marcos.ortiztirado@gmail.com

Esta aplicación web fue la base sobre la que se creó la interfaz del primer Reto Derivatech36, llevado a cabo durante agosto y semptiembre del año 2021.
Las bases del concurso fueron publicadas en https://derivatech.mx/derivatech360/


<div style="background-color:rgba(37, 41, 88); text-align:center; vertical-align: middle; padding:40px 0;">
<img src = "https://derivatech.mx/derivatech360/assets/images/derivatech360.png" height = "100" align = "center"/>
</div>


Para utilizar la aplicación web visita el siguiente enlace: http://motmotm.pythonanywhere.com/

Si lo requiere, utiliza:
* usuario: marcos
* contraseña: derivatech

## Requerimientos

En este proyecto se uitlizaron las librerías `Dash` y `Plotly`para desarrollar la interfaz. Mientras que los datos de los precios de las Acciones y Opciones son obtenidos de Tradier a través de su API.
Se utiliza `Pandas` para el manejo de datos.


## Estrategias

Las estrategias están compuestas por 5 elementos:
* Subyacente: acción en la que está basada la estrategia. Se debe ingresar el Ticker, que es el código de la acción en el mercado. Por ejemplo: `AAPL`, `TSLA` o `MSFT`.
* Precio objetivo (Strike): precio del subyacente que condiciona el éxito de la estrategia.
* Dirección: indica si el precio del subyacente deberá de estar por encima o debajo del precio objetivo.
* Fecha de vencimiento: fecha en la que el subyacente deberá de cumplir con la condición establecida por precio objetivo y dirección.
* Rendimiento: campo calculado con base en el mercado y que depende de todos los elementos anteriores.

Una estrategia es "Exitosa" cuando el precio de la acción finaliza arriba o abajo (dependiendo de la Dirección elegida) del Precio objetivo seleccionado en la fecha de vencimiento al cierre del mercado.

Una estrategia "Exitosa" otorga su rendimiento registrado.

Una estrategia "No exitosa" otorga un rendimiento de -100.00%

## Rendimiento

Las estrategias están compuestas por dos contratos de [Opciones](https://www.investopedia.com/terms/o/optionscontract.asp), un Long Call y un Short Call con un Strike más alto en caso de ser Dirección "Up"; y un Long Put con un Short Put de Strike menor, en caso de ser dirección "Down". Creando así, una estrategia conocida como [Debit Spread](https://www.investopedia.com/terms/d/debitspread.asp). 

Las fechas de vencimiento son determinadas por los contratos de opciones existentes sobre la acción seleccionada. En la mayoría de los casos son cada viernes, excepto en acciones menos líquidas, donde serán únicamente el 3er viernes de cada mes; o de las acciones más líquidas como los etf's de índices, donde podemos encontrar vencimientos en días miércoles.

Una vez seleccionada la fecha de vencimiento, se filtran todos los Strikes disponibles para esa fecha. El Strike seleccionado será la parte corta o short de nuestro Debit Spread, y la parte larga o long será la que construya el Debit Spread con mayor rendimiento. Esto último se lleva a cabo de manera automática.

El rendimiento es calculado de la siguiente manera:

<img src="https://latex.codecogs.com/svg.image?\mathbf{Rendimiento}=\frac{Max&space;Payoff}{Cost}" title="\mathbf{Rendimiento}=\frac{Max Payoff}{Cost}" />

Donde Max Payoff es la ganancia máxima que se obtiene al superar el strike en la fecha de vencimiento y Cost es el costo neto de los contratos de opciones.


