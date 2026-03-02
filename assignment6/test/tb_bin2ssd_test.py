import cocotb
from cocotb.triggers import Timer, ReadOnly

# dictionary
# bruker for å teste funksjonen fra task a
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

async def stimuli_generator(dut):
    # går gjennom alle mulige verdier
    for val in range(2**4):
        await Timer(10, unit='ns')
        dut.di.value = val

async def compare(dut):
    dut._log.info("Starting compare...")
    while True:
        await dut.di.value_change
        await ReadOnly()
        expected = bin2ssd[int(dut.di.value)]
        assert int(dut.abcdefg.value) == expected, \
            f"Fail: Actual value of 'abcdefg={dut.abcdefg.value}' is not matching the expected value of: '{bin(expected)}'"

        dut._log.info(f"Pass with input={dut.di.value}. Output Actual: {dut.abcdefg.value}, expected: {bin(expected)}")

@cocotb.test()
async def main_test(dut):
    dut._log.info("Starting testing...")
    cocotb.start_soon(compare(dut))
    await cocotb.start_soon(stimuli_generator(dut))
    dut._log.info("Testing done. All tests passed")