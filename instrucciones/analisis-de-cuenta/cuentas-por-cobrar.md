# [registro-diario.md] - CUENTAS POR COBRAR (ESTÁNDAR LATAM)

Esta cuenta (Código 1305) representa el derecho de cobro. Según la **NIC 32 y 39**, es un instrumento financiero que debe medirse por su valor de realización.

## 1. Localización del Impuesto (Cálculo Automático)
Para que el **REGISTRO DIARIO** sea global, el monto del "Débito" debe ajustarse según la tasa local:

| País | Impuesto | Tasa (%) | Fórmula de Registro |
| :--- | :--- | :--- | :--- |
| **Panamá** | ITBMS | 7% | `Venta * 1.07` |
| **Colombia** | IVA | 19% | `Venta * 1.19` |
| **México** | IVA | 16% | `Venta * 1.16` |
| **Chile** | IVA | 19% | `Venta * 1.19` |
| **Costa Rica** | IVA | 13% | `Venta * 1.13` |

## 2. Diferencia en Cambio (Multimoneda)
Si la venta se hace en **Dólares (USD)** pero la contabilidad es en moneda local (ej. Pesos):
* Se registra al tipo de cambio del día de la venta.
* Al recibir el pago, si el dólar subió o bajó, la diferencia se ajusta contra la cuenta **4210 (Ingreso Financiero)** o **5305 (Gasto Financiero)**.

## 3. Deterioro de Cartera (Prudencia Global)
Siguiendo la **NIIF 9**, no esperamos a que el cliente "quiebre". Si el análisis de cuentas muestra que una factura tiene más de 90-120 días sin abono, debemos marcarla como "Dudosa Recuperación".

---
**Instrucción para la IA:** Al detectar un registro de venta a crédito, preguntar siempre: "¿En qué país se realiza la operación?" para aplicar el porcentaje de impuesto correcto al saldo de la cuenta por cobrar.
