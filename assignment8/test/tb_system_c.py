"""
tb_system_c.py - Testbenk for oppgave c
Tester self_test + pulse_width_modulator + output_synchronizer sammen.

Sjekker:
1. At output_synchronizer forsinker DIR og EN med 1 klokkeperiode
2. At DIR aldri endrer seg mens EN er høy (H-bro sikkerhet)
3. At self_test kjører gjennom alle ROM-verdier og stopper på 0x00
"""

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, ClockCycles, Timer


@cocotb.test()
async def test_output_sync_delay(dut):
    """Sjekk at output_synchronizer forsinker signalene med 1 klokke"""

    clock = Clock(dut.mclk, 10, units='ns')
    cocotb.start_soon(clock.start())

    # Reset
    dut.reset.value = 1
    await ClockCycles(dut.mclk, 5)
    dut.reset.value = 0
    await ClockCycles(dut.mclk, 2)

    # Samle dir/en verdier over mange klokkesykler
    # Sjekk at synkroniserte verdier er forsinket 1 klokke
    mismatches = 0
    matches = 0
    prev_dir_raw = int(dut.dir_raw.value)
    prev_en_raw = int(dut.en_raw.value)

    for i in range(500):
        await RisingEdge(dut.mclk)
        # Etter klokkeflanken skal synkronisert verdi matche
        # forrige verdi av rå-signalet (1 klokke forsinkelse)
        dir_sync = int(dut.dir_sync.value)
        en_sync = int(dut.en_sync.value)

        if dir_sync == prev_dir_raw and en_sync == prev_en_raw:
            matches += 1
        else:
            mismatches += 1

        prev_dir_raw = int(dut.dir_raw.value)
        prev_en_raw = int(dut.en_raw.value)

    dut._log.info(f"Forsinkelsessjekk: {matches} matcher, {mismatches} avvik")
    assert matches > 400, f"For få matcher: {matches}/500"


@cocotb.test()
async def test_no_short_circuit(dut):
    """Sjekk at DIR aldri endrer seg mens EN er høy (synkronisert)"""

    clock = Clock(dut.mclk, 10, units='ns')
    cocotb.start_soon(clock.start())

    # Reset
    dut.reset.value = 1
    await ClockCycles(dut.mclk, 5)
    dut.reset.value = 0

    prev_dir = 0
    violations = 0
    cycles = 0

    # Kjør gjennom hele selvtesten (alle ROM-verdier)
    while cycles < 30000:
        await RisingEdge(dut.mclk)
        cycles += 1

        dir_now = int(dut.dir_sync.value)
        en_now = int(dut.en_sync.value)

        # Hvis DIR endret seg, sjekk at EN var lav
        if dir_now != prev_dir:
            if en_now == 1:
                violations += 1
                dut._log.error(
                    f"KORTSLUTNING! DIR endret seg mens EN=1 "
                    f"ved syklus {cycles}"
                )

        prev_dir = dir_now

    dut._log.info(f"Sikkerhetssjekk ferdig: {cycles} sykler, {violations} brudd")
    assert violations == 0, f"{violations} kortslutningsbrudd funnet!"


@cocotb.test()
async def test_self_test_sequence(dut):
    """Sjekk at self_test går gjennom ROM og stopper"""

    clock = Clock(dut.mclk, 10, units='ns')
    cocotb.start_soon(clock.start())

    # Reset
    dut.reset.value = 1
    await ClockCycles(dut.mclk, 5)
    dut.reset.value = 0

    # Forventede ROM-verdier
    expected = [
        0x19, 0x32, 0x4B, 0x64, 0x7F, 0x7F,
        0xE7, 0xCE, 0xB6, 0x81, 0x81,
        0x9E, 0xB6,
        0x19, 0x32, 0x4B, 0x64, 0x7F,
        0xE7, 0xCE, 0xB6, 0x9E,
        0x00
    ]

    # Med TICK_LIMIT=99 er hver verdi 100 klokkesykler
    TICK = 100
    seen_values = []

    for i in range(len(expected)):
        # Vent til midt i perioden for stabil avlesning
        await ClockCycles(dut.mclk, TICK // 2)
        val = int(dut.duty_cycle.value)
        seen_values.append(val)
        dut._log.info(f"ROM[{i}] = 0x{val:02X} (forventet 0x{expected[i]:02X})")

        if i < len(expected) - 1:
            # Vent resten av perioden
            await ClockCycles(dut.mclk, TICK - (TICK // 2))

    # Sjekk at alle verdier stemmer
    for i, (got, exp) in enumerate(zip(seen_values, expected)):
        assert got == exp, f"ROM[{i}]: fikk 0x{got:02X}, forventet 0x{exp:02X}"

    dut._log.info("Alle ROM-verdier verifisert!")

    # Sjekk at duty_cycle forblir 0x00 etter sekvensen er ferdig
    await ClockCycles(dut.mclk, TICK * 2)
    final = int(dut.duty_cycle.value)
    assert final == 0x00, f"duty_cycle burde være 0x00 etter ferdig, men er 0x{final:02X}"
    dut._log.info("Self-test stoppet korrekt paa 0x00")
