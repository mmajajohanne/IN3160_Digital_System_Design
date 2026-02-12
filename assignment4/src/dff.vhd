library ieee;
use ieee.std_logic_1164.all;

entity dff is 
  port ( 
    rst_n , mclk : in  std_ulogic;   -- Reset, Clock
    din          : in  std_ulogic;   -- Data in
    dout         : out std_ulogic    -- Data out
  );      
end dff;


architecture rtl of dff is 
  -- Creating a next_<signal> is redundant here, since din can be used directly.
  -- However, it is good practice to name register input as next_<signal>.
  -- Register input should normally be assigned combinationally.
  signal next_dout : std_ulogic; 
begin
  next_dout <= din;
  P_DFF : process(mclk) is
  begin 
    if rising_edge(mclk) then 
      dout <= 
        '0' when rst_n = '0' else
        next_dout;
    end if;
  end process;
end architecture rtl;


-- code below is for demonstration purposes only
/*
architecture VHDL2002_async of dff is 
begin
  P_DFF : process(rst_n, mclk)
  begin
    if rst_n='0' then
      dout <= '0';
    elsif rising_edge(mclk) then
      dout <= din;
    end if;
  end process P_DFF;  
end architecture VHDL2002_async;
*/
/* -- we normally use a process because we update multiple registers using the same triggers
architecture async_reset_oneliner of dff is 
begin
  dout <= '0' when not reset_n else din when rising_edge(clk);
end architecture async_reset_oneliner;
*/