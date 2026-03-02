library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

architecture secret of seg7ctrl is
  signal counter : unsigned(19 downto 0);
  signal sel     : std_logic;

  function bin2ssd_alt(bin : std_logic_vector(3 downto 0)) 
    return std_logic_vector is
    variable seg : std_logic_vector(6 downto 0);
  begin
    case bin is
      when "0000" => seg := "0000000";
      when "0001" => seg := "0011110";
      when "0010" => seg := "0111100";
      when "0011" => seg := "1001111";
      when "0100" => seg := "0001110";
      when "0101" => seg := "0111101";
      when "0110" => seg := "0011101";
      when "0111" => seg := "0010101";
      when "1000" => seg := "0111011";
      when "1001" => seg := "0111110";
      when "1010" => seg := "1110111";
      when "1011" => seg := "0000101";
      when "1100" => seg := "1111011";
      when "1101" => seg := "0011100";
      when "1110" => seg := "0001101";
      when "1111" => seg := "1111111";
      when others => seg := "0000000";
    end case;
    return seg;
  end function bin2ssd_alt;

begin

  process(mclk, reset)
  begin
    if reset = '1' then
      counter <= (others => '0');
    elsif rising_edge(mclk) then
      counter <= counter + 1;
    end if;
  end process;

  sel <= counter(19);
  c   <= sel;

  abcdefg <= bin2ssd_alt(d0) when sel = '0' else
             bin2ssd_alt(d1);

end architecture secret;