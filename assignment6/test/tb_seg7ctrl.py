import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ReadOnly, Timer

# samme dictionary som i tb_bin2ssd
bin2ssd = {
    0b0000: 0b1111110,
    0b0001: 0b0110000,
    0b0010: 0b1101101,
    0b0011: 0b1111001,
    0b0100: 0b0110011,
    0b0101: 0b1011011,
    0b0110: 0b1011111,
    0b0111: 0b1110000,
    0b1000: 0b1111111,
    0b1001: 0b1111011,
    0b1010: 0b1110111,
    0b1011: 0b0011111,
    0b1100: 0b1001110,
    0b1101: 0b0111101,
    0b1110: 0b1001111,
    0b1111: 0b1000111
}

@cocotb.test()
async def test_seg7ctrl(dut):
    """Test at seg7ctrl multiplekser d0 og d1 korrekt"""

    # start klokke: 10 ns periode = 100 MHz
    cocotb.start_soon(Clock(dut.mclk, 10, units="ns").start())

    # reset
    dut.reset.value = 1
    dut.d0.value = 0
    dut.d1.value = 0
    await RisingEdge(dut.mclk)
    await RisingEdge(dut.mclk)
    dut.reset.value = 0

    # test med noen forskjellige d0/d1-kombinasjoner
    test_pairs = [
        (0x3, 0xA),  # 3 og A
        (0x0, 0xF),  # 0 og F
        (0x5, 0x8),  # 5 og 8
        (0x7, 0xC),  # 7 og C
    ]

    for d0_val, d1_val in test_pairs:
        await RisingEdge(dut.mclk)
        dut.d0.value = d0_val
        dut.d1.value = d1_val
        dut._log.info(f"Testing d0={d0_val:#x}, d1={d1_val:#x}")

        # vent på at c skifter til '0' (viser d0)
        while True:
            await RisingEdge(dut.mclk)
            await ReadOnly()
            if int(dut.c.value) == 0:
                break

        # sjekk at abcdefg matcher bin2ssd(d0)
        expected = bin2ssd[d0_val]
        actual = int(dut.abcdefg.value)
        assert actual == expected, \
            f"c=0: abcdefg={actual:#09b}, expected={expected:#09b} for d0={d0_val:#x}"
        dut._log.info(f"  c=0: abcdefg={actual:#09b} matches d0 ✓")

        # vent på at c skifter til '1' (viser d1)
        while True:
            await RisingEdge(dut.mclk)
            await ReadOnly()
            if int(dut.c.value) == 1:
                break

        # sjekk at abcdefg matcher bin2ssd(d1)
        expected = bin2ssd[d1_val]
        actual = int(dut.abcdefg.value)
        assert actual == expected, \
            f"c=1: abcdefg={actual:#09b}, expected={expected:#09b} for d1={d1_val:#x}"
        dut._log.info(f"  c=1: abcdefg={actual:#09b} matches d1 ✓")

    dut._log.info("All tests passed!")