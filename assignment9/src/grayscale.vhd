library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all; 

entity grayscale is
  generic ( N : natural := 8);
  port(
    reset, clk           : in  std_ulogic;
    R, G, B, WR, WG, WB  : in  std_ulogic_vector(N-1 downto 0);
    RGB_valid            : in  std_ulogic;
    Y                    : out std_ulogic_vector(N-1 downto 0);     
    overflow, Y_valid    : out std_ulogic
  );
end entity grayscale;

architecture RTL of grayscale is
  -- steg 1 signaler
  signal i_R, i_G, i_B         : unsigned(2*N-1 downto 0);  -- kombinatorisk
  signal r_R, r_G, r_B         : unsigned(2*N-1 downto 0);  -- register
  signal r_valid_s1            : std_ulogic;
  
  -- steg 2 signaler
  signal next_Y, r_Y               : unsigned(N-1 downto 0);
  signal next_valid, r_valid       : std_ulogic;
  signal next_overflow, r_overflow : std_ulogic;
  
begin
  Y        <= std_ulogic_vector(r_Y);
  overflow <= r_overflow;
  Y_valid  <= r_valid;
  
  REG_ASSIGNMENT: process(clk) is  
  begin 
    if rising_edge(clk) then 
      if reset then 
        r_R        <= (others => '0');
        r_G        <= (others => '0');
        r_B        <= (others => '0');
        r_valid_s1 <= '0';
        r_Y        <= (others => '0');
        r_valid    <= '0';
        r_overflow <= '0';
      else 
        -- steg 1 registre
        r_R        <= i_R;
        r_G        <= i_G;
        r_B        <= i_B;
        r_valid_s1 <= RGB_valid;
        -- steg 2 registre
        r_Y        <= next_Y;
        r_valid    <= next_valid;
        r_overflow <= next_overflow;
      end if;
    end if;
  end process; 
  
  CALCULATION: process (all) is
    variable i_sum      : unsigned(2*N+1 downto 0);
    variable i_overflow : std_ulogic; 
  begin
    -- steg 1: multiplikasjon
    i_R <= unsigned(WR) * unsigned(R);
    i_G <= unsigned(WG) * unsigned(G);
    i_B <= unsigned(WB) * unsigned(B);
    
    -- steg 2: addisjon og overflow
    i_sum := unsigned("00" & r_R) + unsigned("00" & r_G) + unsigned("00" & r_B);
    i_overflow := or(i_sum(i_sum'left downto i_sum'left-1)); 
    next_Y <= (others => '1') when i_overflow else i_sum(2*N-1 downto N);
    next_overflow <= i_overflow;
    next_valid <= r_valid_s1;
  end process;
  
end architecture RTL;
