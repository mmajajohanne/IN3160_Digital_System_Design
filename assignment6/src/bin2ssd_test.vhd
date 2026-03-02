library ieee;
use ieee.std_logic_1164.all;
use work.seg7_pkg.all;

entity bin2ssd_test is
  port (
    di      : in  std_logic_vector(3 downto 0);
    abcdefg : out std_logic_vector(6 downto 0)
  );
end entity bin2ssd_test;

architecture rtl of bin2ssd_test is
begin
  abcdefg <= bin2ssd(di);
end architecture rtl;