-- pwm_system.vhd
-- komplett system for oppgave e:
--   self_test -> PWM -> output_synchronizer      (motor-styring)
--   SA/SB -> input_sync -> quad_decoder -> velocity_reader -> seg7ctrl

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity pwm_system is
  generic(
    TICK_LIMIT   : natural := 300_000_000 - 1;
    FILENAME     : string  := "rom_data.txt";--"../src/rom_data.txt";
    RCOUNT_WIDTH : natural := 20;
    TEN_MS_COUNT : natural := 1_000_000
  );
  port(
    mclk, reset    : in  std_ulogic;
    sa, sb         : in  std_ulogic;
    dir_out, en_out : out std_ulogic;
    abcdefg        : out std_logic_vector(6 downto 0);
    c              : out std_logic
  );
end entity pwm_system;

architecture structural of pwm_system is
  signal duty_cycle_i         : std_ulogic_vector(7 downto 0);
  signal dir_i, en_i          : std_ulogic;
  signal sa_sync_i, sb_sync_i : std_ulogic;
  signal pos_inc_i, pos_dec_i : std_ulogic;
  signal velocity_i           : u_signed(7 downto 0);
  signal abs_vel              : unsigned(7 downto 0);
begin

  abs_vel <= unsigned(abs(velocity_i));

  -- self-test: leser duty_cycle-verdier fra ROM
  st : entity work.self_test
    generic map(
      TICK_LIMIT => TICK_LIMIT,
      FILENAME   => FILENAME
    )
    port map(
      mclk       => mclk,
      reset      => reset,
      duty_cycle => duty_cycle_i
    );

  -- PWM-modul (med PDM submodul)
  pwm : entity work.pulse_width_modulator
    port map(
      mclk       => mclk,
      reset      => reset,
      duty_cycle => duty_cycle_i,
      dir        => dir_i,
      en         => en_i
    );

  -- output-synkronisering
  out_sync : entity work.output_synchronizer
    port map(
      mclk    => mclk,
      reset   => reset,
      dir_in  => dir_i,
      en_in   => en_i,
      dir_out => dir_out,
      en_out  => en_out
    );

  -- input-synkronisering
  in_sync : entity work.input_synchronizer
    port map(
      mclk   => mclk,
      reset  => reset,
      sa_in  => sa,
      sb_in  => sb,
      sa_out => sa_sync_i,
      sb_out => sb_sync_i
    );

  -- Quadrature-dekoder
  quad : entity work.quadrature_decoder
    port map(
      mclk    => mclk,
      reset   => reset,
      sa      => sa_sync_i,
      sb      => sb_sync_i,
      pos_inc => pos_inc_i,
      pos_dec => pos_dec_i
    );

  -- hastighetsberegning
  vel : entity work.velocity_reader
    generic map(
      RCOUNT_WIDTH => RCOUNT_WIDTH,
      TEN_MS_COUNT => TEN_MS_COUNT
    )
    port map(
      mclk     => mclk,
      reset    => reset,
      pos_inc  => pos_inc_i,
      pos_dec  => pos_dec_i,
      velocity => velocity_i
    );

  -- 7-segment display (viser absolutt hastighet)
  seg7 : entity work.seg7ctrl
    port map(
      mclk    => mclk,
      reset   => reset,
      d0      => std_logic_vector(abs_vel(3 downto 0)),
      d1      => std_logic_vector(abs_vel(7 downto 4)),
      abcdefg => abcdefg,
      c       => c
    );

end architecture structural;
