library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

-- importerer pakken
library work;
use work.subprog_pck.all;

entity pargen is 
  generic (
    WIDTH : integer := 16
  );
  port (
    rst_n        : in  std_ulogic;
    mclk         : in  std_ulogic;
    indata1      : in  std_ulogic_vector(WIDTH-1 downto 0);
    indata2      : in  std_ulogic_vector(WIDTH-1 downto 0);
    par          : out std_ulogic);  
end pargen;

architecture rtl of pargen is 
  
  -- interne signaler
  signal toggle_parity, xor_parity, combined_parity : std_ulogic;
  
begin  
  
  -- bruker parity_toggle funksjonen fra pakken
  toggle_parity <= parity_toggle(indata1);
  
  -- bruker parity_xor funksjonen fra pakken
  xor_parity <= parity_xor(indata2);
  
  -- kombinerer 
  combined_parity <= toggle_parity xor xor_parity; 
  
  process (mclk) is    
  begin
    if rising_edge(mclk) then 
      par <= 
        '0' when rst_n = '0' else 
        combined_parity;
    end if;
  end process;
  
end rtl;