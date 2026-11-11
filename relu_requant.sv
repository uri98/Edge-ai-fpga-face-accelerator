module relu_requant #(
    parameter ACC_WIDTH = 24,
    parameter OUT_WIDTH = 8,
    parameter SHIFT_AMT = 7
)(
    input  logic signed [ACC_WIDTH-1:0] acc_in,
    output logic signed [OUT_WIDTH-1:0] data_out
);

    logic signed [ACC_WIDTH-1:0] shifted_val;

    always_comb begin
        if (acc_in <= 0) begin
            data_out = '0;
        end else begin
            shifted_val = acc_in >>> SHIFT_AMT;
            if (shifted_val > 127) begin
                data_out = 8'sd127;
            end else begin
                data_out = shifted_val[OUT_WIDTH-1:0];
            end
        end
    end

endmodule
