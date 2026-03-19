/*
----------------------------------------------------------------------------------------------------
 brief: 
  This module is intended for performing velocity calculations required in Assignment 8, IN3160
  The module shall be applied without modification. Bit widths are targeted our specific lab setup.
  
 file: velocity_reader.vhd
 author: Yngve Hafting
----------------------------------------------------------------------------------------------------
 Copyright (c) 2026 by UiO – University of Oslo (www.uio.no) 
----------------------------------------------------------------------------------------------------
 File history:

 Version | Date       | Author             | Remarks
----------------------------------------------------------------------------------------------------
 1.0     | 2019       | Y.Hafting          | Crafted manually (No AI or generator tool applied)
 1.1     | 2026       | Y.Hafting          | Updated CL/REG separation, naming, unresolved types
         |            |                    |    Function unchanged from 2019. Tested in lab.
----------------------------------------------------------------------------------------------------
*/
library IEEE;
  use IEEE.std_logic_1164.all;
  use IEEE.numeric_std.all;
 
entity velocity_reader is
  generic(
    -- these are made generics for the purpose of testing with a lower clock frequency:
    RCOUNT_WIDTH : natural := 20; -- width of clock dividing down to 100Hz; -- 20 bit should be enough for 100MHz / 10^6 = 100Hz
    TEN_MS_COUNT : natural := 1_000_000 -- number of cycles until 10 ms is reached at 100MHz
  );
  port(
    mclk      : in std_ulogic; 
    reset     : in std_ulogic; 
    pos_inc   : in std_ulogic;
    pos_dec   : in std_ulogic;
    velocity  : out u_signed(7 downto 0) -- rpm value updated every 1/100 s 
  );
end entity velocity_reader;

architecture rtl of velocity_reader is

  -- counts up when count_now is active and resets to 0 when reaching target
  function n_count(current : unsigned; count_now : boolean; target : natural := 9) return unsigned is
  begin
    if count_now then 
      if current >= target then 
        return resize("0", current'length); -- pads with '0's
      else 
        return resize(current + 1, current'length); -- adds one and truncates overflow
      end if;
    else 
      return current; 
    end if;
  end function n_count;

  constant WIDTH : natural := 8;
  constant COUNT_WIDTH : natural := 7; -- width of position counting between -128 and + 127
  
  type shiftreg_type is array( natural range<>) of u_signed(COUNT_WIDTH downto 0);
  signal r_pos_shift, next_pos_shift : shiftreg_type(9 downto 0);  -- 10 shifted values + pos_count - oldest value = 10 count values 

  signal r_pos_count, next_pos_count : u_signed(COUNT_WIDTH downto 0); 
  
  signal r_time_count, next_time_count : u_unsigned(RCOUNT_WIDTH-1 downto 0);
  
  -- signals for detecting errors due to too long counting 
  signal max_pos_count, min_pos_count : std_ulogic;  
  
  signal ten_ms_pulse  : std_ulogic;
  signal pos_count_reset : std_ulogic;
  
  -- moving sum for calculating average velocity / rpms
  signal r_moving_sum, next_moving_sum  : u_signed(COUNT_WIDTH+4 downto 0); -- 9 values + pos_count = 10 values in 100 ms. 
  
  --
  -- 200 pulses per round, 4 pos per pulse => 800 positions per round (ppr)
  -- 800 ppr* 150 rpm = 120 000 positions per min 
  -- 120 000 / 60 = 2 000 positions per second
  -- 200 pos per 1/10s or 20 pos per 1/100s (or 160 pos per 80ms)
  -- +-20 pos count : 6 bit signed
  -- +- 200 pos count : 9 bit signed (use 10 bit for 10 iterations)
  -- 
  
begin
  
  REGISTER_STORAGE: process (mclk, reset) is
  begin
    if reset = '1' then 
      r_pos_count       <= (others => '0');
      r_time_count      <= (others => '0');
      r_moving_sum      <= (others => '0');          
      for i in r_pos_shift'range loop
        r_pos_shift(i)  <= (others => '0');  
      end loop;
    elsif rising_edge(mclk) then 
      r_pos_count  <= next_pos_count;  
      r_time_count <= next_time_count;     
      r_moving_sum <= next_moving_sum;      
      r_pos_shift  <= next_pos_shift;
    end if;  
  end process;

  MOVING_AVG: process(all) is
  begin
    -- default:
    next_moving_sum <= r_moving_sum; 
    next_pos_shift  <= r_pos_shift;
    
    if ten_ms_pulse then                         
      next_moving_sum <= r_moving_sum + r_pos_count - r_pos_shift(r_pos_shift'left); -- = accumulated position count + last count - oldest count
      next_pos_shift(0)  <= r_pos_count;           -- set first shiftregister
      for i in next_pos_shift'left-1 downto next_pos_shift'right loop
        next_pos_shift(i+1) <= r_pos_shift(i);     -- shift all shiftregisters
      end loop;
    end if; 
  end process;

  POSITION_COUNTER: process (all) is
  begin
    if pos_count_reset then 
      next_pos_count <= to_signed(0, next_pos_count'length) + pos_inc - pos_dec; 
    else 
      next_pos_count <= r_pos_count + pos_inc - pos_dec;
    end if;
  end process;
  
  CALC_VELOCITY: process (all)
  begin  
    if (abs(r_moving_sum) > 800-1) then 
      velocity <= to_signed(-127, velocity'length); -- a signal that we are out of bounds
    else 
      -- RPM: (moving_sum * 60sec per min/(0,10sec* 800pos per round) = moving_sum *3/4 rounds per min) 
      -- velocity <= resize( (moving_sum*3)/4, velocity'length ) ;
      
      -- rp10s: (moving_sum * 100 / 800) "Rounds per 10 second" -- does work with 8 bit
      velocity <= resize(r_moving_sum/8, velocity'length); 
    end if;
  end process;
  
  -- max and min pos should never occur, but can be useful during testing 
  max_pos_count <= '1' when ( r_pos_count = ((r_pos_count'left-1)**2 - 1) ) else '0'; -- when we have maximum value 2^size -1 
  min_pos_count <= '1' when ( r_pos_count = -((r_pos_count'left-1)**2) ) else '0'; -- when we have maximum value -2^size   -- should never occur

  -- counter for refreshing velocity calculation
  next_time_count <= n_count( r_time_count, true, TEN_MS_COUNT-1); -- count ten ms, then restart
  ten_ms_pulse <= '1' when (r_time_count = 0) else '0'; -- one clock period high every 10 ms
  
  -- reset position counter every 10ms and at wraparound
  pos_count_reset <= max_pos_count or min_pos_count or ten_ms_pulse; 
  
end architecture rtl;
