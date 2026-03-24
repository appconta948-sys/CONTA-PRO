# PRINCIPIO DE VALUACIÓN O COSTO HISTÓRICO + IMPUESTOS LOCALES

El registro en la **registro-diario.md** debe ajustarse a la normativa fiscal del país de operación. El **Costo del Activo** se registra por su valor de adquisición, y el impuesto se separa según la tasa vigente.

## 1. Matriz de Tasas de Impuesto (IVA / ITBMS / IGV)

Para el cálculo automático en las plantillas, se aplicarán las siguientes tasas generales:

| País | Nombre del Impuesto | Tasa General (%) |
| :--- | :--- | :--- |
| **Argentina** | IVA | 21% |
| **Chile** | IVA | 19% |
| **Colombia** | IVA | 19% |
| **México** | IVA | 16% |
| **Panamá** | ITBMS | 7% |
| **Perú** | IGV | 18% |
| **Uruguay** | IVA | 22% |

## 2. Aplicación en [registro-diario.md] - REGISTRO DIARIO (Ejemplo con IVA 19%)

Si compramos una planta en **Colombia o Chile (19%)**:

| ID | PUC (CÓDIGO) | DETALLE | DÉBITO (+) | CRÉDITO (-) |
| :--- | :--- | :--- | :--- | :--- |
| 003 | `152005` | Planta + Instalación (Costo) | 11.500 | |
| 003 | `240805` | **IVA Descontable (19%)** | **2.185** | |
| 003 | `2335XX` | Total Acreedores | | **13.685** |

## 3. Aplicación en [registro-diario.md] - REGISTRO DIARIO (Ejemplo con ITBMS 7%)

Si la misma compra se hace en **Panamá (7%)**:

| ID | PUC (CÓDIGO) | DETALLE | DÉBITO (+) | CRÉDITO (-) |
| :--- | :--- | :--- | :--- | :--- |
| 003 | `152005` | Planta + Instalación (Costo) | 11.500 | |
| 003 | `240805` | **ITBMS (7%)** | **805** | |
| 003 | `2335XX` | Total Acreedores | | **12.305** |

---
**Instrucción para la IA:** Antes de validar el asiento en la **registro-diario.md**, el sistema debe verificar el país configurado y calcular el impuesto automáticamente sobre la base del costo (Planta + Instalación).

