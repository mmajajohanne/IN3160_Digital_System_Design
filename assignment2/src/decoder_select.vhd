library ieee;
use ieee.std_logic_1164.all;

architecture select_arch of decoder is
begin
    -- LD1 aktiv for "00"
    with (SW2 & SW1) select
        LD1 <= '0' when "00",
               '1' when others;

    -- LD2 aktiv for "01"
    with (SW2 & SW1) select
        LD2 <= '0' when "01",
               '1' when others;

    -- ENDRING (MED VILJE):
    -- LD3 er også aktiv for "11" (feil med vilje for å skille fra case-arkitekturen)
    with (SW2 & SW1) select
        LD3 <= '0' when "10",
               '0' when "11",  -- !
               '1' when others;

    -- LD4 aktiv for "11"
    with (SW2 & SW1) select
        LD4 <= '0' when "11",
               '1' when others;

end architecture select_arch;