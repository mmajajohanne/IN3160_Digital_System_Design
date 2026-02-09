import cocotb
from cocotb.triggers import Timer
from cocotb.clock import Clock

@cocotb.test()
async def main_test(dut):
    dut._log.info("Applying stimuli...")
    
    # Starter med rst_n = 1 ved tid 0ns
    dut.rst_n.value = 1
    
    # Standard indata ved tid 0ns
    dut.indata.value = 0b00000000
    
    # Starter klokke (100ns periode)
    dut._log.info("Starting clock")
    cocotb.start_soon(Clock(dut.mclk, 100, unit="ns").start())
    
    # Venter til 100ns og setter reset (active low)
    await Timer(100, units="ns")
    dut.rst_n.value = 0
    
    # Holder reset aktiv til 200ns og setter til 1
    await Timer(100, units="ns") # 200ns
    dut.rst_n.value = 1
    
    # Venter til 300ns og setter indata = 11110000
    await Timer(100, unit="ns")   # now at 300 ns
    dut.indata.value = 0b11110000
    
    # Venter il 400ns og setter indata = 00001111
    await Timer(100, unit="ns")   # now at 400 ns
    dut.indata.value = 0b00001111
    
    await Timer(800, unit="ns")
    dut._log.info("Stimuli done")
    
    