"""
tb_pwm_system.py - Testbenk for det komplette systemet (oppgave e)

Tester (kun top-level signaler):
  1. H-bro sikkerhet: dir_out endres aldri mens en_out er høy
  2. Motor kjører: en_out pulserer under ROM-sekvensen
  3. Motor stopper: en_out er 0 etter sekvensen er ferdig
"""

import cocotb
from cocotb import start_soon
from cocotb.clock import Clock
from cocotb.triggers import ReadOnly, RisingEdge, ClockCycles

TICK_LIMIT = 1000
ROM_SIZE = 23
CLOCK_PERIOD_NS = 10


async def reset_dut(dut):
    """Reset DUT og vent til systemet er klart"""
    dut._log.info("Resetting...")
    await RisingEdge(dut.mclk)
    dut.reset.value = 1
    dut.sa.value = 0
    dut.sb.value = 0
    await RisingEdge(dut.mclk)
    dut.reset.value = 0
    await RisingEdge(dut.mclk)
    dut._log.info("Reset complete")


@cocotb.test()
async def main_test(dut):
    """Hoved-test: sjekker H-bro sikkerhet, motor aktivitet, og motor stopp"""
    dut._log.info("Starter testing...")
    start_soon(Clock(dut.mclk, CLOCK_PERIOD_NS, unit="ns").start())
    await reset_dut(dut)

    dir_changes = 0
    dir_last = 0
    en_rises = 0
    en_last = 0
    hbro_violations = 0

    # vent hele ROM-sekvensen (23 entries * 1000 sykluser per entry)
    seq_cycles = TICK_LIMIT * ROM_SIZE
    dut._log.info(f"Venter {seq_cycles} sykluser for ROM-sekvensen...")

    for cycle in range(seq_cycles):
        await RisingEdge(dut.mclk)
        await ReadOnly()

        try:
            dir_now = int(dut.dir_out.value)
            en_now = int(dut.en_out.value)
        except ValueError:
            # signal har uinitialiserte verdier (U/X), hopp over
            continue

        # tell retningsendringer (bekrefter at ROM avanserer)
        if dir_now != dir_last:
            if en_now == 1:
                hbro_violations += 1
                dut._log.error(f"Syklus {cycle}: dir endret mens en=1")
            dir_changes += 1
        dir_last = dir_now

        # tell EN-pulser
        if en_now == 1 and en_last == 0:
            en_rises += 1
        en_last = en_now

        # periodisk status (hvert 5000. syklus)
        if cycle > 0 and cycle % 5000 == 0:
            dut._log.info(
                f"  Syklus {cycle}: dir_out={dir_now}, en_out={en_now}, "
                f"dir_endringer={dir_changes}, en_pulser={en_rises}"
            )

    dut._log.info(
        f"ROM-sekvens ferdig: dir_endringer={dir_changes}, en_pulser={en_rises}, "
        f"H-bro brudd={hbro_violations}"
    )

    # --- sjekk: ROM-sekvensen inneholder både positive og negative verdier ---
    # hvis dir aldri endret seg, går ikke ROM videre (TICK_LIMIT ikke satt riktig?)
    if dir_changes == 0:
        dut._log.error(
            "dir_out endret seg ALDRI! "
            "Sjekk at -gTICK_LIMIT=999 faktisk blir brukt i makefilen."
        )

    # --- sjekk: H-bro sikkerhet ---
    assert hbro_violations == 0, (
        f"H-bro kortslutning! dir endret seg {hbro_violations} gang(er) mens en=1"
    )

    # --- sjekk: motor var aktiv ---
    assert en_rises > 0, (
        "en_out pulserte aldri under ROM-sekvensen! Motoren kjoerte ikke. "
        f"dir_endringer={dir_changes}"
    )
    dut._log.info(f"Motor var aktiv med {en_rises} EN-pulser. OK!")

    # --- vent ekstra for at PDM og FSM skal stoppe ---
    # siste ROM-verdi er 0x00, så PWM-FSM går til idle -> en=0
    extra_wait = 3 * TICK_LIMIT
    dut._log.info(f"Venter {extra_wait} ekstra sykluser for motor-stopp...")
    await ClockCycles(dut.mclk, extra_wait)
    await ReadOnly()

    try:
        en_val = int(dut.en_out.value)
    except ValueError:
        en_val = -1  # uinitialisert

    dut._log.info(f"Etter sekvensen + ventetid: en_out = {en_val}")
    assert en_val == 0, f"en_out burde vaere 0 etter sekvensen, fikk {en_val}"

    dut._log.info("Alle tester bestatt!")
