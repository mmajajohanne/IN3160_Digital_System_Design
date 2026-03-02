import os
import cocotb
from cocotb import start_soon
from cocotb.clock import Clock
from cocotb.triggers import Edge, FallingEdge, RisingEdge, Timer, ReadOnly

rom_values = [
        0b00010010, # 1 2
        0b00110100, # 3 4
        0b01000000, # 4 0
        0b00000000, # 0 0
        0b01010110, # 5 6
        0b01110011, # 7 3
        0b00000000, # 0 0
        0b10000110, # 8 6
        0b10010000, # 9 0
        0b00000000, # 0 0
        0b10101011, # A B
        0b00110000, # 3 0
        0b00000000, # 0 0
        0b11000110, # C 6
        0b01100101, # 6 5
        0b00000000  # 0 0
]

bin2ssd_v2 = {
    0b0000: 0b0000000,
    0b0001: 0b0011110,
    0b0010: 0b0111100,
    0b0011: 0b1001111,
    0b0100: 0b0001110,
    0b0101: 0b0111101,
    0b0110: 0b0011101,
    0b0111: 0b0010101,
    0b1000: 0b0111011,
    0b1001: 0b0111110,
    0b1010: 0b1110111,
    0b1011: 0b0000101,
    0b1100: 0b1111011,
    0b1101: 0b0011100,
    0b1110: 0b0001101,
    0b1111: 0b1111111
}
def write_log_info(dut, string):
    # tester å farge teksten grønn for å se bedre i terminalen
    color_start = "\033[32m" 
    color_end = "\033[0m"
    dut._log.info(f"{color_start}{ string }{color_end}")

async def reset_dut(dut):
    write_log_info(dut, "Resetting...")
    await FallingEdge(dut.mclk)
    dut.reset.value = 1
    await RisingEdge(dut.mclk)
    dut.reset.value = 0
    write_log_info(dut, "Resetting complete...")

async def compare(dut):
    write_log_info(dut, "Starting compare...")
    # addresse = dut.adr.value
    while True:
        await RisingEdge(dut.mclk)
        await ReadOnly()
        expected = bin2ssd_v2[int(dut.d0.value)] if dut.c.value == 0 else bin2ssd_v2[int(dut.d1.value)]
        assert int(dut.abcdefg.value) == expected, write_log_info(dut, f"Fail: Actual value of 'abcdefg = {bin(dut.abcdefg.value)}' is not matching the expected value of: '{bin(expected)}'")


@cocotb.test()
async def main_test(dut):
    write_log_info(dut, "Starting testing...")
    start_soon(Clock(dut.mclk, 10, units="ns").start())
    await reset_dut(dut)
    cocotb.start_soon(compare(dut))
    await Timer(1000, units='ns')
    write_log_info(dut,f"Testing done of {os.path.basename(__file__)}...")