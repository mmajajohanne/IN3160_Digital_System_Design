library ieee;
use ieee.std_logic_1164.all;

architecture case_arch of decoder is
    signal s : std_ulogic_vector(1 downto 0);
begin
    s <= SW2 & SW1; 

    process(s)
    begin
        -- default: alle outputs er inaktive (active low = '1')
        LD1 <= '1';
        LD2 <= '1';
        LD3 <= '1';
        LD4 <= '1';

        case s is -- sjekker kombinasjoner av inputene som skal gi 0
            when "00" =>
                LD1 <= '0';

            when "01" =>
                LD2 <= '0';

            when "10" =>
                LD3 <= '0';

            when "11" =>
                LD4 <= '0';

            when others =>
                -- gjør ingenting (default = 1)
                null;
        end case;
    end process;

end architecture case_arch;