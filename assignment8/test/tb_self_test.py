'''
tb_self_test.py: Enkel testbenk for self_test-modulen.
Sjekker at ROM-verdiene kommer ut i riktig rekkefølge
og at modulen stopper etter siste verdi.
'''
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, RisingEdge

# Forventede verdier fra rom_data.txt
EXPECTED = [
    0x19, 0x32, 0x4B, 0x64, 0x7F, 0x7F,
    0xE7, 0xCE, 0xB6, 0x81, 0x81, 0x9E, 0xB6,
    0x19, 0x32, 0x4B, 0x64, 0x7F,
    0xE7, 0xCE, 0xB6, 0x9E,
    0x00
]

# TICK_LIMIT settes til 99 via generic, saa en tick = 100 sykluser
TICK = 100

@cocotb.test()
async def test_self_test_rom(dut):
    '''Sjekk at alle ROM-verdier kommer ut i riktig rekkefølge'''

    cocotb.start_soon(Clock(dut.mclk, 10, 'ns').start())

    # Reset
    dut.reset.value = 1
    await ClockCycles(dut.mclk, 5)
    dut.reset.value = 0
    await ClockCycles(dut.mclk, 5)

    # Foerste verdi skal vaere EXPECTED[0] etter reset
    val = int(dut.duty_cycle.value)
    dut._log.info(f"Verdi 0: 0x{val:02X}")
    assert val == EXPECTED[0], f"Forventet 0x{EXPECTED[0]:02X}, fikk 0x{val:02X}"

    # Step gjennom resten av ROM
    for i in range(1, len(EXPECTED)):
        await ClockCycles(dut.mclk, TICK)
        await ClockCycles(dut.mclk, 3)
        val = int(dut.duty_cycle.value)
        dut._log.info(f"Verdi {i}: 0x{val:02X}")
        assert val == EXPECTED[i], (
            f"Verdi {i}: Forventet 0x{EXPECTED[i]:02X}, fikk 0x{val:02X}")

    # Sjekk at den stopper paa 0x00
    await ClockCycles(dut.mclk, TICK * 3)
    val = int(dut.duty_cycle.value)
    assert val == 0x00, f"Modulen stoppet ikke! Fikk 0x{val:02X}"
    dut._log.info("Self-test stoppet korrekt paa 0x00")
