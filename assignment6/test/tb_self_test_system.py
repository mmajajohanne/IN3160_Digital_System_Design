import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ReadOnly

# alternativ kode-tabell fra oppgave c)
bin2ssd_alt = {
    0x0: 0b0000000,
    0x1: 0b0011110,
    0x2: 0b0111100,
    0x3: 0b1001111,
    0x4: 0b0001110,
    0x5: 0b0111101,
    0x6: 0b0011101,
    0x7: 0b0010101,
    0x8: 0b0111011,
    0x9: 0b0111110,
    0xA: 0b1110111,
    0xB: 0b0000101,
    0xC: 0b1111011,
    0xD: 0b0011100,
    0xE: 0b0001101,
    0xF: 0b1111111,
}

# forventet ROM-innhold
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
async def test_self_test_system(dut):
    """Test at self_test_system viser riktige segmentverdier"""

    cocotb.start_soon(Clock(dut.mclk, 10, units="ns").start())

    # Reset
    dut.reset.value = 1
    await RisingEdge(dut.mclk)
    await RisingEdge(dut.mclk)
    dut.reset.value = 0

    for i, (exp_d1, exp_d0) in enumerate(expected_rom):
        # vent på second_tick
        while True:
            await RisingEdge(dut.mclk)
            await ReadOnly()
            try:
                if int(dut.self_test_inst.second_tick.value) == 1:
                    break
            except AttributeError:
                # fallback: vent fast antall sykluser
                break

        # vent en syklus til for registre
        await RisingEdge(dut.mclk)
        await ReadOnly()

        # les c og sjekk abcdefg mot riktig verdi
        c_val = int(dut.c.value)
        actual = int(dut.abcdefg.value)

        if c_val == 0:
            expected = bin2ssd_alt[exp_d0]
            label = f"d0={exp_d0:#x}"
        else:
            expected = bin2ssd_alt[exp_d1]
            label = f"d1={exp_d1:#x}"

        assert actual == expected, \
            f"Index {i}, c={c_val}: abcdefg={actual:#09b}, expected={expected:#09b}"
        dut._log.info(f"Index {i}: c={c_val}, {label}, abcdefg={actual:#09b} ✓")

    dut._log.info("All tests passed!")