`timescale 1ns / 1ps

module edge_ai_tb;

    // 1. Declaración de señales de estímulo y monitoreo
    logic        clk;
    logic        rst_n;
    logic        start_infer;
    logic        done_infer;
    logic        face_match;
    logic [7:0]  debug_out;

    // Variables para medir latencia en tiempo real
    time start_time, end_time;

    // 2. Instancia de tu Acelerador Edge AI (DUT - Device Under Test)
    edge_ai_top dut (
        .clk         (clk),
        .rst_n       (rst_n),
        .start_infer (start_infer),
        .done_infer  (done_infer),
        .face_match  (face_match),
        .debug_out   (debug_out)
    );

    // 3. Generador de reloj de 50 MHz (Periodo = 20 ns)
    initial begin
        clk = 0;
        forever #10 clk = ~clk;
    end

    // 4. Secuencia principal de prueba y verificación
    initial begin
        // Inicialización de señales
        rst_n       = 0;
        start_infer = 0;

        $display("==========================================================");
        $display(" INICIANDO SIMULACION DE ACELERADOR EDGE AI (CYCLONE V)   ");
        $display("==========================================================");

        // Soltamos el reset después de 50 ns
        #50;
        rst_n = 1;
        #40;

        // Disparamos el pulso para procesar la matriz 32x32
        $display("[%0t ns] Enviando pulso start_infer...", $time);
        start_time  = $time;
        start_infer = 1;
        #20;
        start_infer = 0;

        // Esperamos a que el hardware termine los 1024 ciclos MAC
        wait(done_infer == 1'b1);
        end_time = $time;

        // Mostramos los resultados de latencia y hardware en consola
        #20;
        $display("==========================================================");
        $display(" INFERENCIA COMPLETADA EN HARDWARE PURO                   ");
        $display(" -> Tiempo total (Latencia): %0t ns (%.2f microsegundos)", 
                 (end_time - start_time), (end_time - start_time) / 1000.0);
        $display(" -> Valor INT8 calculado (debug_out): %0d", $signed(debug_out));
        $display(" -> Resultado Biometrico (face_match): %b", face_match);
        $display("==========================================================");

        #100;
        $stop; // Detiene la simulación en Questa / ModelSim
    end

endmodule
