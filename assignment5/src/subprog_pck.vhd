-- Subprogram Package for Parity utregning
library ieee;
use ieee.std_logic_1164.all;

-- PACKAGE DECLARATION
package subprog_pck is
  
  -- funksjon 1: Toggle
  function parity_toggle(data : std_ulogic_vector) return std_ulogic;
  
  -- funksjon 2: XOR
  function parity_xor(data : std_ulogic_vector) return std_ulogic;
  
end package subprog_pck;

-- PACKAGE BODY
package body subprog_pck is
  
  -- implementasjon av toggle
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
  
  -- implementasjon av XOR
  function parity_xor(data : std_ulogic_vector) return std_ulogic is
  begin
    return xor(data);
  end function;
  
end package body subprog_pck;