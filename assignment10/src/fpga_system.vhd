-- fpga_system.vhd
-- toppnivå for oppgave 10: system-on-chip integrasjon.
-- duty_cycle er nå en inngang fra zynq-prosessoren via axi-gpio.
-- self_test er fjernet; velocity er lagt til som utgang slik at prosessoren kan lese hastigheten.

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity fpga_system is
  port(
    mclk, reset     : in  std_ulogic;
    duty_cycle      : in  std_logic_vector(7 downto 0);
    sa, sb          : in  std_ulogic;
    velocity        : out std_logic_vector(7 downto 0);
    dir_out, en_out : out std_ulogic;
    abcdefg         : out std_logic_vector(6 downto 0);
    c               : out std_logic
  );
end entity fpga_system;

architecture structural of fpga_system is
  signal duty_cycle_i         : std_ulogic_vector(7 downto 0);
  signal dir_i, en_i          : std_ulogic;
  signal sa_sync_i, sb_sync_i : std_ulogic;
  signal pos_inc_i, pos_dec_i : std_ulogic;
  signal velocity_i           : u_signed(7 downto 0);
  signal abs_vel              : unsigned(7 downto 0);
begin

  duty_cycle_i <= std_ulogic_vector(duty_cycle);
  velocity     <= std_logic_vector(velocity_i);
  abs_vel      <= unsigned(abs(velocity_i));

  -- pulsbreddemodulator
  pwm : entity work.pulse_width_modulator
    port map(
      mclk       => mclk,
      reset      => reset,
      duty_cycle => duty_cycle_i,
      dir        => dir_i,
      en         => en_i
    );

  -- utgangssynkronisering
  out_sync : entity work.output_synchronizer
    port map(
      mclk    => mclk,
      reset   => reset,
      dir_in  => dir_i,
      en_in   => en_i,
      dir_out => dir_out,
      en_out  => en_out
    );

  -- inngangsynkronisering for encoder-signaler
  in_sync : entity work.input_synchronizer
    port map(
      mclk   => mclk,
      reset  => reset,
      sa_in  => sa,
      sb_in  => sb,
      sa_out => sa_sync_i,
      sb_out => sb_sync_i
    );

  -- quadrature-dekoder
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
      RCOUNT_WIDTH => 20,
      TEN_MS_COUNT => 1_000_000
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
      mclk    => std_logic(mclk),
      reset   => std_logic(reset),
      d0      => std_logic_vector(abs_vel(3 downto 0)),
      d1      => std_logic_vector(abs_vel(7 downto 4)),
      abcdefg => abcdefg,
      c       => c
    );

end architecture structural;
