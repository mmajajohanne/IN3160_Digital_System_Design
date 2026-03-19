'''
tb_self_test.py: Enkel testbenk for self_test-modulen.
Sjekker at ROM-verdiene kommer ut i riktig rekkefølge
og at modulen stopper etter siste verdi.
'''
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, RisingEdge, Timer

# Forventede verdier fra rom_data.txt (hex -> signed desimal)
EXPECTED = [
    0x19, 0x32, 0x4B, 0x64, 0x7F, 0x7F,
    0xE7, 0xCE, 0xB6, 0x81, 0x81, 0x9E, 0xB6,
    0x19, 0x32, 0x4B, 0x64, 0x7F,
    0xE7, 0xCE, 0xB6, 0x9E,
    0x00
]

@cocotb.test()
async def test_self_test_rom(dut):
    '''Sjekk at alle ROM-verdier kommer ut i riktig rekkefølge'''

    # Start klokke
    cocotb.start_soon(Clock(dut.mclk, 10, 'ns').start())

    # Reset
    dut.reset.value = 1
    await ClockCycles(dut.mclk, 5)
    dut.reset.value = 0
    await ClockCycles(dut.mclk, 2)

    # Foerste verdi skal vaere EXPECTED[0] rett etter reset
    val = dut.duty_cycle.value.to_unsigned()
    dut._log.info(f"Verdi 0: 0x{val:02X}")
    assert val == EXPECTED[0], f"Forventet 0x{EXPECTED[0]:02X}, fikk 0x{val:02X}"

    # TICK_LIMIT er satt til 99 i simulering (via generic),
    # saa vi venter 100 klokkesykluser per verdi
    TICK = 100

    for i in range(1, len(EXPECTED)):
        await ClockCycles(dut.mclk, TICK)
        # Gi et par ekstra sykluser for registeret
        await ClockCycles(dut.mclk, 3)
        val = dut.duty_cycle.value.to_unsigned()
        dut._log.info(f"Verdi {i}: 0x{val:02X}")
        assert val == EXPECTED[i], (
            f"Verdi {i}: Forventet 0x{EXPECTED[i]:02X}, fikk 0x{val:02X}")

    # Sjekk at den STOPPER (holder 0x00 etter siste verdi)
    await ClockCycles(dut.mclk, TICK * 3)
    val = dut.duty_cycle.value.to_unsigned()
    assert val == 0x00, f"Modulen stoppet ikke! Fikk 0x{val:02X}"
    dut._log.info("Self-test stoppet korrekt paa 0x00")
