# [puc-latam.md] - CODIFICADOR INTELIGENTE

> **ESTADO:** Activo (Versión 1.0)
> **FUNCIÓN:** Validación de códigos para el REGISTRO DIARIO.

## Lógica de Validación (Lo que la IA debe vigilar):

* **Si el código empieza por 1 (ACTIVO):** Verifica que el dinero esté entrando al negocio o que sea un bien físico.
* **Si el código empieza por 2 (PASIVO):** Verifica que sea una deuda o el impuesto (IVA/ITBMS) recaudado.
* **Si el código empieza por 4 (INGRESOS):** ¡Felicidades! Hubo una venta. Se anota en el CRÉDITO.
* **Si el código empieza por 5 (GASTOS):** Es la salida necesaria para operar. Se anota en el DÉBITO.
