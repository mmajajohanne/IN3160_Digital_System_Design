import cocotb
from cocotb.triggers import RisingEdge, Timer
from cocotb.clock import Clock


@cocotb.test()
async def test_shiftn(dut):

    dut._log.info("Starting shiftn sim (64-bit)")

    dut.rst_n.value = 1
    dut.serial_in.value = 0

    cocotb.start_soon(Clock(dut.mclk, 100, units="ns").start())

    await Timer(100, units="ns")
    dut.rst_n.value = 0

    await Timer(100, units="ns")
    dut.rst_n.value = 1

    await RisingEdge(dut.mclk)

    bitstream = [1,0,1,1,0,0,1,0]

    for bit in bitstream:
        dut.serial_in.value = bit
        await RisingEdge(dut.mclk)


    for _ in range(64):
        await RisingEdge(dut.mclk)

    dut._log.info("Sim completed")