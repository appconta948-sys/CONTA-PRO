# [registro-diario.md] - GUÍA DE IMPUESTOS POR PAÍS (CÓDIGO 24xx)

Para que el sistema de "el lento" sea global, debemos parametrizar el nombre del impuesto según la bandera donde opere:

| País | Impuesto al Consumo (IVA) | Impuesto a la Renta (Empresas) | Ente Recaudador |
| :--- | :--- | :--- | :--- |
| **Panamá** | **ITBMS** (7%, 10%, 15%) | **ISR** (25%) | **DGI** |
| **Colombia** | **IVA** (19%) | **Renta** (35%) | **DIAN** |
| **México** | **IVA** (16%) | **ISR** (30%) | **SAT** |
| **Chile** | **IVA** (19%) | **IDPC** (25% - 27%) | **SII** |
| **Argentina** | **IVA** (21%) | **Ganancias** (25% - 35%) | **AFIP** |
| **Costa Rica** | **IVA** (13%) | **Renta** (5% - 30%) | **Hacienda** |

## 1. La Trampa del IVA/ITBMS (Crédito vs. Débito)
En toda Latam funciona igual:
* **Débito Fiscal (Pasivo +):** Lo que le cobras al cliente.
* **Crédito Fiscal (Activo -):** Lo que le pagaste a tus proveedores.
* **NETO POR PAGAR:** La resta de ambos. Si el Crédito es mayor, tienes un "Saldo a Favor" (Activo).

## 2. Retenciones en la Fuente (El "Pago Anticipado")
En países como Colombia o México, cuando "el lento" le paga a un proveedor, el Estado le obliga a **quitarle un pedacito** de ese pago y guardarlo para el gobierno. 
* Esto se llama **Retenciones por Pagar**. Es un pasivo que se debe entregar al mes siguiente.

## 3. Impuestos Municipales (Locales)
* **Panamá:** Tesorería Municipal (Tablas por actividad).
* **Colombia:** ICA (Industria y Comercio).
* **México:** Impuesto sobre Nómina (Estatal).
