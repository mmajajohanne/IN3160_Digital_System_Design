library ieee;
use ieee.std_logic_1164.all;

entity output_synchronizer is
  port(
    mclk  : in  std_ulogic;
    reset : in  std_ulogic;
    -- usynkroniserte innganger (fra PWM)
    dir_in  : in  std_ulogic;
    en_in   : in  std_ulogic;
    -- synkroniserte utganger (til H-bro)
    dir_out : out std_ulogic;
    en_out  : out std_ulogic
  );
end entity output_synchronizer;

architecture rtl of output_synchronizer is
begin
  process(mclk) is
  begin
    if rising_edge(mclk) then
      if reset = '1' then
        dir_out <= '0';
        en_out  <= '0';
      else
        dir_out <= dir_in;
        en_out  <= en_in;
      end if;
    end if;
  end process;
end architecture rtl;
