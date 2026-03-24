# PRINCIPIO DE UNIDAD DE MEDIDA (APLICACIÓN GLOBAL)

Este principio es el eje transversal de todo el sistema. **Ningún reporte, tabla o anexo** es válido si no especifica la moneda en la que se expresan sus valores.

## 1. Aplicación en todas las Plantillas

El sistema de GitHub debe incluir el campo de **Moneda Local** en las siguientes estructuras obligatorias:

### [registro-diario.md] - REGISTRO DIARIO
* **Regla:** Todos los asientos (Débitos y Créditos) se registran en la moneda funcional del país de operación.
* **Ejemplo:** Si el ente es de **Colombia**, toda la Tabla 1 se llena en **COP**.

### [libro-mayor.md] - LIBRO MAYOR (Saldos)
* **Regla:** Los totales acumulados por cuenta del PUC deben reflejar la moneda local para permitir la consolidación.

### [PLANTILLAS DE ESTADOS FINANCIEROS]
* **Balance General:** Debe indicar en el encabezado: *"Expresado en [Moneda Local] (ISO)"*.
* **Estado de Resultados:** Debe mantener la misma unidad de medida para que la utilidad sea real.

## 2. Tabla de Referencia de Monedas (Configuración del Sistema)

| Territorio | Unidad de Medida | ISO | Símbolo |
| :--- | :--- | :--- | :--- |
| **Colombia** | Peso Colombiano | **COP** | $ |
| **México** | Peso Mexicano | **MXN** | $ |
| **Panamá** | Balboa / Dólar | **PAB/USD** | B/. / $ |
| **Chile** | Peso Chileno | **CLP** | $ |
| **Perú** | Sol | **PEN** | S/ |
| **Argentina** | Peso Argentino | **ARS** | $ |
| **España / UE** | Euro | **EUR** | € |
| **Ecuador / USA**| Dólar Estadounidense| **USD** | $ |

## 3. Control de Errores para el Usuario
1. **No mezclar:** No se permite sumar `100 USD` + `500.000 COP` en la misma columna. 
2. **Conversión Obligatoria:** Si hay una compra en el extranjero, se debe usar la tasa de cambio para llevar el valor a la moneda de la plantilla correspondiente.

---
**Instrucción para la IA:** Todas las plantillas generadas a partir de este punto deben heredar la **Unidad de Medida** definida en la configuración inicial del repositorio.
