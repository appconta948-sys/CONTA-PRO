# [registro-diario.md] - INVENTARIO DE MERCANCÍA (CÓDIGO 1435)

Esta cuenta identifica el valor de los bienes listos para la venta. Según la **NIC 2**, los inventarios deben valorarse al **Costo** o al **Valor Neto Realizable** (el menor).

## 1. ¿Qué incluimos en el "Costo" (Visión Latam)?
No es solo el precio de factura. Para que el **REGISTRO DIARIO** sea exacto, el costo incluye:
* **Precio de compra:** Lo que le pagaste al proveedor.
* **Aranceles de importación:** (Impuestos no recuperables).
* **Transporte y Manejo:** Fletes y seguros para que la mercancía llegue a tu bodega.
* **Menos:** Descuentos o rebajas comerciales.

## 2. Dinámica de "Espera de Consumo" (Clave UP)
El inventario es un **Activo Corriente** mientras esté en el estante. 
* **Aumenta (DÉBITO +):** Cuando compras o te devuelven mercancía en buen estado.
* **Disminuye (CRÉDITO -):** Cuando vendes (se traslada al **Costo de Ventas**) o cuando la mercancía se daña/vence.

## 3. Métodos de Valuación Globales
Para que el sistema funcione en cualquier país, "el lento" debe elegir un método (en el archivo de configuración):
1. **PEPS / FIFO:** (Primero en Entrar, Primero en Salir). Ideal para productos con vencimiento (alimentos, medicinas).
2. **Promedio Ponderado:** El más usado en Latam por su sencillez y estabilidad tributaria.

---
**⚠️ REGLA DE ORO GLOBAL:** Si la mercancía se daña o pasa de moda y ya no se puede vender al precio original, se debe registrar una **Pérdida por Deterioro**, bajando el valor en el **REGISTRO DIARIO**.
