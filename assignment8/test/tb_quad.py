"""
tb_quad.py - Testbenk for quadrature_decoder (oppgave d)

Tester:
1. Forward-rotasjon: SA/SB gaar 00->01->11->10->00 => pos_inc pulser
2. Reverse-rotasjon: SA/SB gaar 00->10->11->01->00 => pos_dec pulser
3. Ingen bevegelse: SA/SB forblir konstant => ingen pulser
4. Feil-deteksjon: hopp over en tilstand => gaar til s_reset
5. Reset-oppfoersel: sjekk at reset nuller alt
"""

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ClockCycles

# Quadrature-sekvenser (SA, SB)
FORWARD_SEQ  = [(0, 0), (0, 1), (1, 1), (1, 0)]  # increment-retning
REVERSE_SEQ  = [(0, 0), (1, 0), (1, 1), (0, 1)]  # decrement-retning

# State-konverteringstabell (for debugging)
state_conv_table = {
    0: 's_reset',
    1: 's_init',
    2: 's_0',
    3: 's_1',
    4: 's_2',
    5: 's_3'
}


async def reset_dut(dut):
    """Reset og vent til stabil tilstand"""
    dut.reset.value = 1
    dut.sa.value = 0
    dut.sb.value = 0
    await ClockCycles(dut.mclk, 5)
    dut.reset.value = 0
    # Vent saa FSM-en gaar gjennom s_reset -> s_init -> s_0
    await ClockCycles(dut.mclk, 3)


async def set_ab_and_wait(dut, sa, sb):
    """Sett SA/SB og vent 1 klokkesyklus saa FSM-en oppdateres"""
    dut.sa.value = sa
    dut.sb.value = sb
    await RisingEdge(dut.mclk)


@cocotb.test()
async def test_forward_rotation(dut):
    """Sjekk at forward-sekvens gir pos_inc pulser"""
    clock = Clock(dut.mclk, 10, unit='ns')
    cocotb.start_soon(clock.start())

    await reset_dut(dut)

    inc_total = 0
    dec_total = 0

    # Roter fremover 4 hele runder (4 steg per runde)
    # Start-tilstand er s_0 (AB=00), saa foerste overgang er til 01
    for runde in range(4):
        for sa, sb in FORWARD_SEQ:
            await set_ab_and_wait(dut, sa, sb)
            # Sjekk registrerte utganger (forsinket 1 klokke)
            await RisingEdge(dut.mclk)
            if dut.pos_inc.value == 1:
                inc_total += 1
            if dut.pos_dec.value == 1:
                dec_total += 1

    dut._log.info(f"Forward: inc={inc_total}, dec={dec_total}")
    assert inc_total > 0, "Ingen pos_inc pulser ved forward-rotasjon!"
    assert dec_total == 0, f"Uventede pos_dec pulser: {dec_total}"


@cocotb.test()
async def test_reverse_rotation(dut):
    """Sjekk at reverse-sekvens gir pos_dec pulser"""
    clock = Clock(dut.mclk, 10, unit='ns')
    cocotb.start_soon(clock.start())

    await reset_dut(dut)

    inc_total = 0
    dec_total = 0

    # Roter bakover 4 hele runder
    for runde in range(4):
        for sa, sb in REVERSE_SEQ:
            await set_ab_and_wait(dut, sa, sb)
            await RisingEdge(dut.mclk)
            if dut.pos_inc.value == 1:
                inc_total += 1
            if dut.pos_dec.value == 1:
                dec_total += 1

    dut._log.info(f"Reverse: inc={inc_total}, dec={dec_total}")
    assert dec_total > 0, "Ingen pos_dec pulser ved reverse-rotasjon!"
    assert inc_total == 0, f"Uventede pos_inc pulser: {inc_total}"


@cocotb.test()
async def test_no_movement(dut):
    """Sjekk at ingen bevegelse gir null pulser"""
    clock = Clock(dut.mclk, 10, unit='ns')
    cocotb.start_soon(clock.start())

    await reset_dut(dut)

    # Vent mange sykler uten aa endre SA/SB
    inc = 0
    dec = 0
    for _ in range(100):
        await RisingEdge(dut.mclk)
        if dut.pos_inc.value == 1:
            inc += 1
        if dut.pos_dec.value == 1:
            dec += 1

    dut._log.info(f"Ingen bevegelse: inc={inc}, dec={dec}")
    assert inc == 0, f"Falske pos_inc pulser: {inc}"
    assert dec == 0, f"Falske pos_dec pulser: {dec}"


@cocotb.test()
async def test_error_detection(dut):
    """Sjekk at et hopp over en tilstand trigger feil (gaar gjennom s_reset)"""
    clock = Clock(dut.mclk, 10, unit='ns')
    cocotb.start_soon(clock.start())

    await reset_dut(dut)

    # Vi er naa i s_0 (AB=00). Hopp til AB=11 (ugyldig, hopper over 01 og 10)
    dut.sa.value = 1
    dut.sb.value = 1

    # Sjekk at FSM-en recoverer: gaar gjennom s_reset -> s_init -> s_2
    # Vi venter nok klokkeflanker og sjekker at vi ender i s_2 (AB=11)
    saw_reset = False
    for i in range(5):
        await RisingEdge(dut.mclk)
        state_val = int(dut.state.value)
        state_name = state_conv_table.get(state_val, f"unknown({state_val})")
        dut._log.info(f"  Syklus {i+1}: state = {state_name}")
        if state_val == 0:  # s_reset
            saw_reset = True

    # Til slutt skal vi vaere i s_2 (fordi AB=11 og FSM-en har recoveret)
    state_val = int(dut.state.value)
    state_name = state_conv_table.get(state_val, f"unknown({state_val})")
    dut._log.info(f"Endelig tilstand: {state_name}")
    assert state_val == 4, f"Forventet s_2 (4) etter recovery, fikk {state_name}"


@cocotb.test()
async def test_reset_clears_state(dut):
    """Sjekk at reset bringer FSM-en tilbake til s_reset"""
    clock = Clock(dut.mclk, 10, unit='ns')
    cocotb.start_soon(clock.start())

    await reset_dut(dut)

    # Roter litt for aa komme i en annen tilstand
    await set_ab_and_wait(dut, 0, 1)
    await RisingEdge(dut.mclk)

    state_before = int(dut.state.value)
    dut._log.info(f"Foer reset: state = {state_conv_table.get(state_before, '?')}")
    assert state_before != 0, "Burde ikke vaere i s_reset foer reset"

    # Aktiver reset
    dut.reset.value = 1
    await ClockCycles(dut.mclk, 2)

    state_after = int(dut.state.value)
    state_name = state_conv_table.get(state_after, f"unknown({state_after})")
    dut._log.info(f"Etter reset: state = {state_name}")
    assert state_after == 0, f"Forventet s_reset (0), fikk {state_name}"
