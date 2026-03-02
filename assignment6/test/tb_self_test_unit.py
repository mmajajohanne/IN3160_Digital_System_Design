import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ReadOnly

# forventet ROM-innhold: (d1, d0) for hver index
expected_rom = [
    (0x1, 0x2),
    (0x3, 0x4),
    (0x4, 0x0),
    (0x0, 0x0),
    (0x5, 0x6),
    (0x7, 0x3),
    (0x0, 0x0),
    (0x8, 0x6),
    (0x9, 0x0),
    (0x0, 0x0),
    (0xA, 0xB),
    (0x3, 0x0),
    (0x0, 0x0),
    (0xC, 0x6),
    (0x6, 0x5),
    (0x0, 0x0),
]

@cocotb.test()
async def test_self_test_unit(dut):
    """Test at self_test_unit stepper gjennom ROM korrekt"""

    cocotb.start_soon(Clock(dut.mclk, 10, units="ns").start())

    # Reset
    dut.reset.value = 1
    await RisingEdge(dut.mclk)
    await RisingEdge(dut.mclk)
    dut.reset.value = 0

    # sjekk alle 16 ROM-entries
    for i, (exp_d1, exp_d0) in enumerate(expected_rom):

        # vent på at second_tick fyrer (TICK_LIMIT + 1 sykluser)
        while True:
            await RisingEdge(dut.mclk)
            await ReadOnly()
            if int(dut.second_tick.value) == 1:
                break

        # vent en klokkesyklus til, registrene oppdateres på neste flanke
        await RisingEdge(dut.mclk)
        await ReadOnly()

        actual_d0 = int(dut.d0.value)
        actual_d1 = int(dut.d1.value)

        assert actual_d1 == exp_d1 and actual_d0 == exp_d0, \
            f"Index {i}: d1={actual_d1:#x}, d0={actual_d0:#x}, " \
            f"expected d1={exp_d1:#x}, d0={exp_d0:#x}"

        dut._log.info(
            f"Index {i}: d1={actual_d1:#x}, d0={actual_d0:#x} ✓"
        )

    dut._log.info("All ROM entries verified!")