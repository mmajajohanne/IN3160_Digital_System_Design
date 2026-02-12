import cocotb
from cocotb.triggers import Timer, RisingEdge
from cocotb.clock import Clock


@cocotb.test()
async def test_shift32(dut):
    dut._log.info("Starting shift32 test")

    # initialverdier ved tid 0
    dut.rst_n.value = 1        
    dut.serial_in.value = 0

    # start klokke (100 ns periode)
    cocotb.start_soon(Clock(dut.mclk, 100, units="ns").start())

    # aktiver reset (active low)
    await Timer(100, units="ns")
    dut._log.info("Applying reset")
    dut.rst_n.value = 0

    # hold reset i én klokkeperiode
    await Timer(100, units="ns")
    dut.rst_n.value = 1
    dut._log.info("Releasing reset")

    # vent på en høy klokkeflanke etter reset
    await RisingEdge(dut.mclk)

    # sender inn serial bitsekvens
    bitstream = [1, 0, 1, 1, 0, 0, 1, 0]

    for bit in bitstream:
        dut.serial_in.value = bit
        dut._log.info(f"serial_in = {bit}")
        await RisingEdge(dut.mclk)

        dut._log.info(
            f"q = {dut.q.value.binstr}, serial_out = {int(dut.serial_out.value)}"
        )

    # lar den skifte lengre videre
    for _ in range(32):
        await RisingEdge(dut.mclk)
        dut._log.info(
            f"q = {dut.q.value.binstr}, serial_out = {int(dut.serial_out.value)}"
        )

    dut._log.info("Shift register test completed")