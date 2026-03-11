import random
import cocotb
from cocotb.triggers import RisingEdge, FallingEdge, Timer, ReadOnly
from cocotb.clock import Clock
from cocotb.utils import get_sim_time

CLOCK_PERIOD_NS = 10
WIDTH = 16


# sjekk: pulsen er aldri PÅ lenger enn max_on + 1 sykluser (fra oppgaven)
async def max_on_check(dut):
    while True:
        await RisingEdge(dut.pdm_pulse)          # puls slås PÅ
        start = get_sim_time('ns')
        await FallingEdge(dut.pdm_pulse)          # puls slås AV
        end = get_sim_time('ns')
        cycles = (end - start) / CLOCK_PERIOD_NS
        assert cycles <= int(dut.max_on.value) + 1, (
            f"Pulse ON for {cycles} cycles, max allowed: {int(dut.max_on.value) + 1}")


# sjekk: pulsen er aldri AV kortere enn min_on (litt forvirret over om det egentlig skal være min_off her)
# måler AV-tid: FallingEdge → RisingEdge
async def min_off_check(dut):
    while True:
        await FallingEdge(dut.pdm_pulse)          # puls slås AV
        start = get_sim_time('ns')
        await RisingEdge(dut.pdm_pulse)           # puls slås PÅ igjen
        end = get_sim_time('ns')
        cycles = (end - start) / CLOCK_PERIOD_NS
        assert cycles >= int(dut.min_on.value), (
            f"Pulse OFF for {cycles} cycles, minimum: {int(dut.min_on.value)}")


# sjekk: mea_ack er aldri høy mens pdm_pulse er høy
# sjekker hvert klokkesyklus med ReadOnly for å unngå delta-delay-problemer
async def mea_ack_during_pulse_check(dut):
    while True:
        await RisingEdge(dut.clk)
        await ReadOnly()
        if dut.pdm_pulse.value == 1:
            assert dut.mea_ack.value == 0, (
                "mea_ack asserted while pdm_pulse is high!")


# sjekk: mea_ack settes høy innen 2 klokkesykluser etter mea_req
# når pulsen allerede er lav, hvis pulsen er høy når mea_req kommer, venter man til pulsen er ferdig først
async def mea_ack_assert_check(dut):
    while True:
        await RisingEdge(dut.mea_req)

        # vent til pulsen er lav — det er først da kravet gjelder
        while True:
            await RisingEdge(dut.clk)
            await ReadOnly()
            if dut.pdm_pulse.value == 0:
                break

        # nå er pulsen lav, mea_ack skal komme innen 2 sykluser
        for _ in range(2):
            await RisingEdge(dut.clk)
            await ReadOnly()
            if dut.mea_ack.value == 1:
                break

        assert dut.mea_ack.value == 1, (
            "mea_ack not asserted within 2 cycles after mea_req (with pulse low)")


# sjekk: mea_ack settes lav innen 2 klokkesykluser etter mea_req går lav
async def mea_ack_deassert_check(dut):
    while True:
        await FallingEdge(dut.mea_req)

        for _ in range(2):
            await RisingEdge(dut.clk)
            await ReadOnly()
            if dut.mea_ack.value == 0:
                break

        assert dut.mea_ack.value == 0, (
            "mea_ack not de-asserted within 2 cycles after mea_req went low")


# sjekk: duty cycle er innen 10% av setpoint
# måles fra FallingEdge til neste FallingEdge (én periode)
# forventet duty cycle = setpoint / 2^WIDTH
async def duty_cycle_check(dut):
    while True:
        # start måling ved fallende flanke
        await FallingEdge(dut.pdm_pulse)
        period_start = get_sim_time('ns')
        expected_duty = int(dut.setpoint.value) / (2 ** WIDTH)

        # vent på stigende flanke (puls PÅ)
        await RisingEdge(dut.pdm_pulse)
        on_start = get_sim_time('ns')

        # vent på fallende flanke (puls AV igjen)
        await FallingEdge(dut.pdm_pulse)
        period_end = get_sim_time('ns')

        on_time = period_end - on_start
        total_time = period_end - period_start

        if total_time > 0:
            measured_duty = on_time / total_time
            assert abs(measured_duty - expected_duty) <= 0.10, (
                f"Duty cycle {measured_duty:.2%} not within 10% of "
                f"expected {expected_duty:.2%}")


# stimulus
@cocotb.test()
async def pdm_test(dut):
    """Main test for PDM module"""

    cocotb.start_soon(Clock(dut.clk, CLOCK_PERIOD_NS, units='ns').start())

    # reset
    dut.reset.value = 1
    dut.mea_req.value = 0
    dut.setpoint.value = 0
    dut.min_on.value = 5
    dut.min_off.value = 10
    dut.max_on.value = 200
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.reset.value = 0
    await RisingEdge(dut.clk)

    # start alle kontinuerlige sjekker
    cocotb.start_soon(max_on_check(dut))
    cocotb.start_soon(min_off_check(dut))
    cocotb.start_soon(mea_ack_during_pulse_check(dut))
    cocotb.start_soon(mea_ack_assert_check(dut))
    cocotb.start_soon(mea_ack_deassert_check(dut))
    cocotb.start_soon(duty_cycle_check(dut))

    # velg tilfeldige tidspunkter for mea_req (5 stk, 400+ sykluser mellom)
    mea_req_times = sorted(random.sample(range(5, 45), 5))

    # test 50 tilfeldige setpoint-verdier
    for i in range(50):
        setpoint_val = random.randint(1, 2 ** WIDTH - 2)  # unngå 0 og maks
        dut.setpoint.value = setpoint_val

        # de første 10 testes i 3+ perioder (trenger mer tid)
        if i < 10:
            await Timer(2000 * CLOCK_PERIOD_NS, units='ns')
        else:
            await Timer(500 * CLOCK_PERIOD_NS, units='ns')

        # sjekk om man skal sende mea_req denne iterasjonen
        if i in mea_req_times:
            # bent til pulsen er lav før man setter mea_req
            if dut.pdm_pulse.value == 1:
                await FallingEdge(dut.pdm_pulse)

            dut.mea_req.value = 1

            # vent på mea_ack
            await RisingEdge(dut.mea_ack)

            # hold mea_req høy i 5 sykluser etter mea_ack
            for _ in range(5):
                await RisingEdge(dut.clk)

            dut.mea_req.value = 0

            # vent litt ekstra mellom mea_req-hendelser (400+ sykluser)
            await Timer(400 * CLOCK_PERIOD_NS, units='ns')

    dut._log.info("All tests completed successfully!")