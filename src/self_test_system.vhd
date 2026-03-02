library ieee;
use ieee.std_logic_1164.all;

entity self_test_system is
  port (
    mclk    : in  std_logic;
    reset   : in  std_logic;
    abcdefg : out std_logic_vector(6 downto 0);
    c       : out std_logic
  );
end entity self_test_system;

architecture structural of self_test_system is

  -- interne signaler som kobler modulene
  signal d0 : std_logic_vector(3 downto 0);
  signal d1 : std_logic_vector(3 downto 0);

begin

  -- self test unit: genererer d0 og d1 fra ROM
  self_test_inst : entity work.self_test_unit
    port map (
      mclk  => mclk,
      reset => reset,
      d0    => d0,
      d1    => d1
    );

  -- seg7ctrl med secret-arkitekturen: dekoder og multiplekser
  seg7ctrl_inst : entity work.seg7ctrl(secret)
    port map (
      mclk    => mclk,
      reset   => reset,
      d0      => d0,
      d1      => d1,
      abcdefg => abcdefg,
      c       => c
    );

end architecture structural;