import cocotb
import random
from cocotb import start_soon
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, ReadOnly

async def reset_dut(dut):
    await FallingEdge(dut.mclk)
    dut.rst_n.value = 0
    dut.indata1.value = 0
    dut.indata2.value = 0
    await RisingEdge(dut.mclk)
    dut.rst_n.value = 1

def parity(value):
    result = 0
    value_int = int(value)
    for _ in range(len(value)):
        result = result ^ (value_int & 1)
        value_int = value_int >> 1
    return result

def predict(dut):
    pred_parity_indata1 = parity(dut.indata1.value)
    pred_parity_indata2 = parity(dut.indata2.value)
    pred_par = pred_parity_indata1 ^ pred_parity_indata2
    return pred_par

# OPPGAVE D: modifisert stimuli_generator
async def stimuli_generator(dut):
    n = 20  # minst 20 verdier
    for i in range(n):
        await FallingEdge(dut.mclk)
        dut.indata1.value = random.getrandbits(16)  # tilfeldig 16-bit verdi
        dut.indata2.value = i                        # teller oppover: 0,1,2,...
        await RisingEdge(dut.mclk)
    # venter en ekstra klokke
    await RisingEdge(dut.mclk)

# OPPGAVE E: compare funksjonen
async def compare(dut):
    # hopp over første syklus etter reset
    await RisingEdge(dut.mclk)
    
    while True:
        # venter til falling edge
        await FallingEdge(dut.mclk)
        await ReadOnly()
        
        # beregner hva par skal bli ved NESTE rising edge
        expected_par = predict(dut)
        
        # venter på rising edge
        await RisingEdge(dut.mclk)
        await ReadOnly()
        
        # sjekk at par ble oppdatert riktig
        assert dut.par.value == expected_par, \
            f"par feil! Fikk {dut.par.value}, forventet {expected_par}"
        
        # sjekk kombinatoriske signaler
        expected_toggle = parity(dut.indata1.value)
        assert dut.toggle_parity.value == expected_toggle, \
            f"toggle_parity feil! Fikk {dut.toggle_parity.value}, forventet {expected_toggle}"
        
        expected_xor = parity(dut.indata2.value)
        assert dut.xor_parity.value == expected_xor, \
            f"xor_parity feil! Fikk {dut.xor_parity.value}, forventet {expected_xor}"

@cocotb.test()
async def main_test(dut):
    dut._log.info("Running test...")
    start_soon(Clock(dut.mclk, 100, unit="ns").start())
    await reset_dut(dut)
    cocotb.start_soon(compare(dut))
    await start_soon(stimuli_generator(dut))
    dut._log.info("Running test... done")