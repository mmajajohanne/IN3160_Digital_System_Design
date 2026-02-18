---pargen.vhd for oppgave b
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

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
  
  -- FUNKSJONER
  
  -- funksjon 1: toggle-metoden
  function parity_toggle(data : std_ulogic_vector) return std_ulogic is
    variable toggle : std_ulogic;
  begin
    toggle := '0';
    for i in data'range loop
      if data(i) = '1' then
        toggle := not toggle;
      end if;
    end loop;
    return toggle;
  end function;
  
  -- funksjon 2: xOR reduction-metoden
  function parity_xor(data : std_ulogic_vector) return std_ulogic is
  begin
    return xor(data);
  end function;
  
  
  -- INTERNE SIGNALER
  signal toggle_parity, xor_parity, combined_parity : std_ulogic;
  
begin  
  
  -- metode 1: bruker parity_toggle funksjonen
  toggle_parity <= parity_toggle(indata1);
  
  -- metode 2: bruker parity_xor funksjonen
  xor_parity <= parity_xor(indata2);
  
  -- kombinerer med xor operatorer
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