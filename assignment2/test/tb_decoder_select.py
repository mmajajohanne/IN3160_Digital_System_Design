import cocotb
from cocotb.triggers import Timer

@cocotb.test()
async def test_all_switch_combinations_select(dut):
    """
    test for select arkitekturen.
    inkluderer en endring i forventet LED-endringer for å sjekke ift. case filen

    inputs: SW2, SW1
    outputs: LD4, LD3, LD2, LD1  (active low)
    """

    # (SW2, SW1, expected_LD4, expected_LD3, expected_LD2, expected_LD1)
    vectors = [
        (0, 0, 1, 1, 1, 0),
        (0, 1, 1, 1, 0, 1),
        (1, 0, 1, 0, 1, 1),
        # endring: LD3 er også active (0) når SW2SW1 = "11"
        (1, 1, 0, 0, 1, 1),
    ]

    for sw2, sw1, ld4, ld3, ld2, ld1 in vectors:
        dut.SW2.value = sw2
        dut.SW1.value = sw1

        await Timer(10, unit="ns")
        
        assert int(dut.LD4.value) == ld4, f"SW2={sw2}, SW1={sw1}: LD4 wrong"
        assert int(dut.LD3.value) == ld3, f"SW2={sw2}, SW1={sw1}: LD3 wrong"
        assert int(dut.LD2.value) == ld2, f"SW2={sw2}, SW1={sw1}: LD2 wrong"
        assert int(dut.LD1.value) == ld1, f"SW2={sw2}, SW1={sw1}: LD1 wrong"
    await Timer(10, unit="ns")
    dut._log.info("All tests passed (select).") 