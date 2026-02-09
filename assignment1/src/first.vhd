library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;

entity first is
  port(
    clk, reset: in std_ulogic;
    up: in std_ulogic;                
    load:  in std_ulogic;                     
    inp:   in  std_ulogic_vector(3 downto 0); 
    count: out std_ulogic_vector(3 downto 0); 
    max_count: out std_ulogic;
    min_count: out std_ulogic                 
  );
end first;

architecture RTL of first is
  -- Declarative region
  signal next_count : u_unsigned(3 downto 0);
begin 
  -- Statement region
  -- Combinational logic used for register input
  next_count <= 
    unsigned(inp) when load = '1' else 
    unsigned(count) + 1 when up = '1' else
    unsigned(count) -1;

  -- register assignment process should only reset or assign next_value(s)
  -- type casting is OK, because it does not infer combinational logic  
  REGISTERS: process (clk) is
  begin   
     if rising_edge(clk) then
       count <=  
         (others => '0') when reset else   -- Synchronous reset
         std_logic_vector(next_count);
     end if;
  end process;

  -- Concurrent signal assignment 
  max_count <= 
    '1' when (up = '1' and count = "1111") else 
    '0';
  
  min_count <=
    '1' when (up = '0' and count = "0000") else
    '0';
end RTL;