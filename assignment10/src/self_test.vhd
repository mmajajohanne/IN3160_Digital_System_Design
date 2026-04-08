library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use std.textio.all;

entity self_test is
  generic(
    TICK_LIMIT : natural := 300_000_000 - 1;  -- 3 sek ved 100 MHz
    FILENAME   : string  := "rom_data.txt"--"../src/rom_data.txt"
  );
  port(
    mclk       : in  std_ulogic;
    reset      : in  std_ulogic;
    duty_cycle : out std_ulogic_vector(7 downto 0)
  );
end entity self_test;

architecture rtl of self_test is

  constant ROM_SIZE : natural := 23;

  type rom_type is array(0 to ROM_SIZE - 1) of
    std_ulogic_vector(7 downto 0);

  -- Les ROM-verdier fra tekstfil (hex-format, én verdi per linje)
  impure function init_rom return rom_type is
    file     rom_file : text open read_mode is FILENAME;
    variable rom_line : line;
    variable tmp      : std_logic_vector(7 downto 0);
    variable rom      : rom_type;
  begin
    for i in rom_type'range loop
      readline(rom_file, rom_line);
      hread(rom_line, tmp);
      rom(i) := std_ulogic_vector(tmp);
    end loop;
    return rom;
  end function;

  constant ROM : rom_type := init_rom;

  signal tick_counter : natural range 0 to TICK_LIMIT := 0;
  signal tick         : std_ulogic := '0';
  signal rom_addr     : natural range 0 to ROM_SIZE - 1 := 0;
  signal done         : std_ulogic := '0';

begin

  TICK_GEN : process(mclk) is
  begin
    if rising_edge(mclk) then
      if reset = '1' then
        tick_counter <= 0;
        tick         <= '0';
      elsif done = '0' then
        if tick_counter = TICK_LIMIT then
          tick_counter <= 0;
          tick         <= '1';
        else
          tick_counter <= tick_counter + 1;
          tick         <= '0';
        end if;
      else
        tick <= '0';
      end if;
    end if;
  end process TICK_GEN;

  ADDR_CTR : process(mclk) is
  begin
    if rising_edge(mclk) then
      if reset = '1' then
        rom_addr <= 0;
        done     <= '0';
      elsif tick = '1' and done = '0' then
        if rom_addr = ROM_SIZE - 1 then
          done <= '1';
        else
          rom_addr <= rom_addr + 1;
        end if;
      end if;
    end if;
  end process ADDR_CTR;

  duty_cycle <= ROM(rom_addr);

end architecture rtl;
