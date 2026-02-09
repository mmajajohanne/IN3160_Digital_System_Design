# tb_variables_vs_signals.py
#
# Testbench made to show the difference between signals and variables
# Students should not have to make changes here

import cocotb
from cocotb.triggers import Timer


@cocotb.test()
async def main_test(dut):
    
    """Try accessing the design."""
    dut._log.info("Running test...")

    # indata 0 at time 0 ns
    dut.indata.value = 0b0

    # Changing indata after 100 ns
    await Timer(100, unit='ns')
    dut.indata.value = 0b1

    # Changing indata after 200 ns
    await Timer(100, unit='ns')
    dut.indata.value = 0b0

    await Timer(100, unit='ns')
    dut._log.info("Test done!")