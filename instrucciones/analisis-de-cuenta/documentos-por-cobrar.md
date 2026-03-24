# [registro-diario.md] - DOCUMENTOS POR COBRAR (EFECTOS)

Esta cuenta (Código 1310) representa derechos de cobro respaldados por documentos de crédito legales. Según la **NIC 32**, es un activo financiero con fecha de vencimiento exigible.

## 1. ¿Qué constituye un "Documento" en Latam?
Para que "el lento" lo anote aquí y no en "Clientes", debe existir uno de estos:
* **Letra de Cambio:** Orden incondicional de pago (Muy común en Panamá y Centroamérica).
* **Pagaré:** Promesa firmada de pagar una suma en una fecha fija (Uso global).
* **Factura Cambiaria:** Factura que por ley se convierte en título valor (Común en Colombia/Chile).

## 2. Diferencia con la Cuenta por Cobrar (Clave UP)
| Característica | Cuenta por Cobrar (1305) | Documento por Cobrar (1310) |
| :--- | :--- | :--- |
| **Respaldo** | Factura / Nota de Entrega | Letra de Cambio / Pagaré |
| **Fuerza Legal** | Comercial | Ejecutiva (Juicio rápido) |
| **Intereses** | Raramente genera | Suele incluir intereses de mora |

## 3. Dinámica en el REGISTRO DIARIO (Global)
* **Registro Inicial (DÉBITO +):** Se anota por el valor nominal del documento + el impuesto local (IVA/ITBMS).
* **Vencimiento:** Si el cliente no paga en la fecha grabada en el documento, se debe reclasificar como "Documento Vencido" para análisis de cobro jurídico.

---
**Regla de Oro Global:** "Papelito habla". Si no hay firma de letra o pagaré, el registro se queda en la cuenta `1305`. Si hay firma, se mueve a la `1310`.
