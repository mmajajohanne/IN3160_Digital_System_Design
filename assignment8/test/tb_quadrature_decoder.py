"""
Tester:
  1. Forward-rotasjon:  SA/SB i gray code 00->01->11->10 => pos_inc pulser
  2. Reverse-rotasjon:  SA/SB i gray code 00->10->11->01 => pos_dec pulser
  3. Feil-deteksjon:    hopp over tilstand => FSM går til s_reset
  4. Bakgrunnsmonitorer:
     - check_reset:   s_reset -> s_init på neste klokke
     - check_pos_neg: pos_inc og pos_dec aldri høy samtidig
"""

import cocotb
from cocotb import start_soon
from cocotb.clock import Clock
from cocotb.triggers import ReadOnly, FallingEdge, RisingEdge

# for å lese state-signalet i waveform
state_conv_table = {
    0: 's_reset',
    1: 's_init',
    2: 's_0',
    3: 's_1',
    4: 's_2',
    5: 's_3'
}


async def reset_dut(dut):
    """Reset DUT og vent til FSM er klar"""
    dut._log.info("Resetting...")
    await RisingEdge(dut.mclk)
    dut.reset.value = 1
    dut.sa.value = 0
    dut.sb.value = 0
    await RisingEdge(dut.mclk)
    dut.reset.value = 0
    await RisingEdge(dut.mclk)
    dut._log.info("Reset complete")


async def set_ab(dut, a, b):
    """Sett SA/SB på fallende flanke (unngår setup/hold-problemer)"""
    await FallingEdge(dut.mclk)
    dut.sa.value = a
    dut.sb.value = b


# ---- bakgrunnsmonitorer ----

async def check_reset(dut):
    """Sjekker at FSM alltid går s_reset -> s_init"""
    while True:
        await RisingEdge(dut.mclk)
        await ReadOnly()
        if dut.state.value == 0:  # s_reset
            await RisingEdge(dut.mclk)
            await ReadOnly()
            assert dut.state.value == 1, (
                f"Forventet s_init etter s_reset, fikk "
                f"{state_conv_table[int(dut.state.value)]}")


async def check_pos_neg(dut):
    """Sjekker at pos_inc og pos_dec aldri er høy samtidig"""
    while True:
        await RisingEdge(dut.mclk)
        await ReadOnly()
        assert not (dut.pos_inc.value == 1 and dut.pos_dec.value == 1), (
            "pos_inc og pos_dec er begge høy samtidig!")


# ---- sekvensielle sjekker ----

async def check_forward(dut):
    """Sjekker at forward gray code gir pos_inc pulser"""
    dut._log.info("Tester forward-rotasjon...")

    # start i s_0 (AB=00)
    await set_ab(dut, 0, 0)
    await RisingEdge(dut.mclk)
    await RisingEdge(dut.mclk)
    await ReadOnly()
    assert dut.state.value == 2, (
        f"Forventet s_0, fikk {state_conv_table[int(dut.state.value)]}")

    # Forward: 00 -> 01 -> 11 -> 10
    forward = [(0, 1), (1, 1), (1, 0)]
    expected_states = [3, 4, 5]  # s_1, s_2, s_3

    for (a, b), exp in zip(forward, expected_states):
        await set_ab(dut, a, b)
        # vent på rising edge før vi sjekker pos_inc
        await RisingEdge(dut.mclk)
        await ReadOnly()
        assert dut.pos_inc.value == 1, (
            f"Forventet pos_inc=1 ved overgang til "
            f"{state_conv_table[exp]}, fikk {dut.pos_inc.value}")
        assert dut.state.value == exp, (
            f"Forventet {state_conv_table[exp]}, fikk "
            f"{state_conv_table[int(dut.state.value)]}")

    dut._log.info("Forward OK")


async def check_reverse(dut):
    """Sjekker at reverse gray code gir pos_dec pulser"""
    dut._log.info("Tester reverse-rotasjon...")

    # start i s_0 (AB=00)
    await set_ab(dut, 0, 0)
    await RisingEdge(dut.mclk)
    await RisingEdge(dut.mclk)
    await ReadOnly()
    assert dut.state.value == 2, (
        f"Forventet s_0, fikk {state_conv_table[int(dut.state.value)]}")

    # reverse: 00 -> 10 -> 11 -> 01
    reverse = [(1, 0), (1, 1), (0, 1)]
    expected_states = [5, 4, 3]  # s_3, s_2, s_1

    for (a, b), exp in zip(reverse, expected_states):
        await set_ab(dut, a, b)
        # registrerte utganger: vent på rising edge før vi sjekker pos_dec
        await RisingEdge(dut.mclk)
        await ReadOnly()
        assert dut.pos_dec.value == 1, (
            f"Forventet pos_dec=1 ved overgang til "
            f"{state_conv_table[exp]}, fikk {dut.pos_dec.value}")
        assert dut.state.value == exp, (
            f"Forventet {state_conv_table[exp]}, fikk "
            f"{state_conv_table[int(dut.state.value)]}")

    dut._log.info("Reverse OK")


async def check_error(dut):
    """Sjekker at ugyldige overganger sender FSM til s_reset"""
    dut._log.info("Tester feil-deteksjon...")

    # ugyldig: hopp over en tilstand
    # 00->11, 11->00, 01->10, 10->01
    transitions = [(0, 0, 1, 1), (1, 1, 0, 0), (0, 1, 1, 0), (1, 0, 0, 1)]

    for a, b, c, d in transitions:
        await set_ab(dut, a, b)
        await RisingEdge(dut.mclk)
        await RisingEdge(dut.mclk)
        await set_ab(dut, c, d)
        await RisingEdge(dut.mclk)
        await ReadOnly()
        assert dut.state.value == 0, (
            f"Forventet s_reset ved {a}{b}->{c}{d}, fikk "
            f"{state_conv_table[int(dut.state.value)]}")

    dut._log.info("Feil-deteksjon OK")


@cocotb.test()
async def main_test(dut):
    """Hoved-test: starter monitorer og kjører sjekkrer sekvensielt"""
    dut._log.info("Starter testing...")
    start_soon(Clock(dut.mclk, 10, unit="ns").start())
    await reset_dut(dut)

    cocotb.start_soon(check_reset(dut))
    cocotb.start_soon(check_pos_neg(dut))

    await check_forward(dut)
    await check_reverse(dut)
    await check_error(dut)

    dut._log.info("Alle tester bestatt!")
