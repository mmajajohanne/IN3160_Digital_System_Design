library ieee;
use ieee.std_logic_1164.all;

entity seg7ctrl is
  port (
    mclk    : in  std_logic;
    reset   : in  std_logic;
    d0      : in  std_logic_vector(3 downto 0);
    d1      : in  std_logic_vector(3 downto 0);
    abcdefg : out std_logic_vector(6 downto 0);
    c       : out std_logic
  );
end entity seg7ctrl;