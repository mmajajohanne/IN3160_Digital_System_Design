library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use work.seg7_pkg.all;

architecture rtl of seg7ctrl is
  signal counter : unsigned(19 downto 0);  -- 20-bit teller, f = 100 MHz / 2^20 = 95 Hz
begin

  -- klokket prosess: teller med asynkron reset
  process(mclk, reset)
  begin
    if reset = '1' then
      counter <= (others => '0');
    elsif rising_edge(mclk) then
      counter <= counter + 1;
    end if;
  end process;

  -- MSB av telleren velger display
  c <= counter(19);

  -- kombinatorisk multiplekser + dekoder
  abcdefg <= bin2ssd(d0) when counter(19) = '0' else
             bin2ssd(d1);

end architecture rtl;