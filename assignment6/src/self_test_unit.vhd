library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity self_test_unit is
  port (
    mclk  : in  std_logic;
    reset : in  std_logic;
    d0    : out std_logic_vector(3 downto 0);
    d1    : out std_logic_vector(3 downto 0)
  );
end entity self_test_unit;

architecture rtl of self_test_unit is

  -- ROM type: array av 8-bit verdier (d1 & d0 pakket sammen)
  type rom_type is array (0 to 15) of std_logic_vector(7 downto 0);

  constant MESSAGE_ROM : rom_type := (
    x"12",  -- index 0:  d1=1, d0=2
    x"34",  -- index 1:  d1=3, d0=4
    x"40",  -- index 2:  d1=4, d0=0
    x"00",  -- index 3:  d1=0, d0=0
    x"56",  -- index 4:  d1=5, d0=6
    x"73",  -- index 5:  d1=7, d0=3
    x"00",  -- index 6:  d1=0, d0=0
    x"86",  -- index 7:  d1=8, d0=6
    x"90",  -- index 8:  d1=9, d0=0
    x"00",  -- index 9:  d1=0, d0=0
    x"AB",  -- index 10: d1=A, d0=B
    x"30",  -- index 11: d1=3, d0=0
    x"00",  -- index 12: d1=0, d0=0
    x"C6",  -- index 13: d1=C, d0=6
    x"65",  -- index 14: d1=6, d0=5
    x"00"   -- index 15: d1=0, d0=0
  );

  -- justerbar grense for second tick (lavere for simulering)
  constant TICK_LIMIT : natural := 100_000_000 - 1;

  signal tick_counter : natural range 0 to TICK_LIMIT;
  signal second_tick  : std_logic;
  signal rom_addr     : unsigned(3 downto 0);

begin

  -- second tick generator
  process(mclk, reset)
  begin
    if reset = '1' then
      tick_counter <= 0;
      second_tick  <= '0';
    elsif rising_edge(mclk) then
      if tick_counter = TICK_LIMIT then
        tick_counter <= 0;
        second_tick  <= '1';
      else
        tick_counter <= tick_counter + 1;
        second_tick  <= '0';
      end if;
    end if;
  end process;

  -- adressepeker som stepper gjennom ROM
  process(mclk, reset)
  begin
    if reset = '1' then
      rom_addr <= (others => '0');
    elsif rising_edge(mclk) then
      if second_tick = '1' then
        rom_addr <= rom_addr + 1;  -- wrapper automatisk 15 -> 0
      end if;
    end if;
  end process;

  -- ROM-lesing og output-registre
  process(mclk, reset)
  begin
    if reset = '1' then
      d0 <= (others => '0');
      d1 <= (others => '0');
    elsif rising_edge(mclk) then
      if second_tick = '1' then
        d1 <= MESSAGE_ROM(to_integer(rom_addr))(7 downto 4);
        d0 <= MESSAGE_ROM(to_integer(rom_addr))(3 downto 0);
      end if;
    end if;
  end process;

end architecture rtl;