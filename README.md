# ⚡ Edge AI Hardware Accelerator: Face Recognition Core

![Python](https://shields.io)
![PyTorch](https://shields.io)
![SystemVerilog](https://shields.io)
![Intel FPGA](https://shields.io)

Núcleo acelerador de inteligencia artificial en el borde (**Edge AI**) diseñado para ejecutar reconocimiento facial biométrico directamente en **hardware digital puro (Intel Cyclone V FPGA)**. Traduce una red neuronal convolucional entrenada en **PyTorch** a circuitos lógicos sintetizables en **SystemVerilog**, logrando una latencia determinista de **~20.5 microsegundos** sin sistema operativo, sin CPU externa y con cero dependencia de la nube.

---

## 🧠 Flujo de Ingeniería (De Python a Silicio)

```text
┌─────────────────┐    ┌──────────────────┐    ┌──────────────────┐    ┌────────────────────────┐
│  PyTorch Model  │───>│  INT8 Quantizer  │───>│ BRAM M10K (.hex) │───>│ SystemVerilog Pipeline │
│  (32x32 Gray)   │    │  (Python Script) │    │  (Intel Quartus) │    │  (MAC + ReLU + Match)  │
└─────────────────┘    └──────────────────┘    └──────────────────┘    └────────────────────────┘
```

1. **Modelo Consciente del Hardware (`Pytorch_IA_code/`):** Arquitectura `HardwareMicroFaceNet` diseñada sin sesgos (*bias-free*) para maximizar la eficiencia de bloques multiplicadores DSP y minimizar el uso de memoria interna.
2. **Compilador / Cuantizador (`exportar_a_fpga.py`):** Script propio que extrae los tensores en punto flotante (`FP32`), los escala a enteros con signo de 8 bits (`INT8`, rango `[-127, 127]`) y genera archivos de inicialización de memoria (`.hex`).
3. **Acelerador RTL (`SystemVerilog/`):** Arquitectura hardware sintetizada en **Intel Quartus Prime**:
   * `mac_unit.sv`: Unidad *Multiply-Accumulate* (`INT8` con acumulador de `24 bits`) mapeada sobre bloques DSP físicos.
   * `relu_requant.sv`: Función de activación combinacional `ReLU` y re-escalado por desplazamiento aritmético de bits (`>>>`).
   * `bram_memory.sv`: Inferencia de memoria interna **M10K** inicializada con `$readmemh`.
   * `edge_ai_top.sv` & `edge_ai_tb.sv`: Máquina de estados finitos (FSM) de control y banco de pruebas de verificación temporal.

---

## 📊 Especificaciones Técnicas

| Parámetro | Especificación |
| :--- | :--- |
| **Arquitectura Destino** | Intel Cyclone V FPGA (`5CEBA2` / `5CEBA4`) |
| **Entrada Biométrica** | Matriz facial de `32 × 32` píxeles en escala de grises (`INT8`) |
| **Aritmética Hardware** | Punto fijo `INT8` (acumulación interna de `24 bits`) |
| **Frecuencia de Reloj** | `50 MHz` (Periodo = `20 ns`) |
| **Latencia de Inferencia** | `~20.5 µs` (`1,024` ciclos de reloj deterministas) |
