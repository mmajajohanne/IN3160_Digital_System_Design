-- system_c_top.vhd
-- Testbar top-level for oppgave c:
-- self_test -> pulse_width_modulator -> output_synchronizer
--
-- Eksponerer mellomliggende signaler (dir_raw, en_raw) slik at
-- testbenken kan verifisere forsinkelsen fra output_synchronizer.

library ieee;
use ieee.std_logic_1164.all;

entity system_c_top is
  generic(
    TICK_LIMIT : natural := 300_000_000 - 1;
    FILENAME   : string  := "../src/rom_data.txt"
  );
  port(
    mclk       : in  std_ulogic;
    reset      : in  std_ulogic;
    -- Self-test utgang (synlig for testbenk)
    duty_cycle : out std_ulogic_vector(7 downto 0);
    -- Rå PWM-utganger (før synkronisering)
    dir_raw    : out std_ulogic;
    en_raw     : out std_ulogic;
    -- Synkroniserte utganger (til H-bro)
    dir_sync   : out std_ulogic;
    en_sync    : out std_ulogic
  );
end entity system_c_top;

architecture rtl of system_c_top is
  signal duty_i    : std_ulogic_vector(7 downto 0);
  signal dir_raw_i : std_ulogic;
  signal en_raw_i  : std_ulogic;
begin

  -- Self-test ROM-sekvens
  self_test_inst : entity work.self_test
    generic map(
      TICK_LIMIT => TICK_LIMIT,
      FILENAME   => FILENAME
    )
    port map(
      mclk       => mclk,
      reset      => reset,
      duty_cycle => duty_i
    );

  -- PWM-modul (med PDM submodul)
  pwm_inst : entity work.pulse_width_modulator
    port map(
      mclk       => mclk,
      reset      => reset,
      duty_cycle => duty_i,
      dir        => dir_raw_i,
      en         => en_raw_i
    );

  -- Output-synkronisering (flipflopper på DIR og EN)
  out_sync_inst : entity work.output_synchronizer
    port map(
      mclk    => mclk,
      reset   => reset,
      dir_in  => dir_raw_i,
      en_in   => en_raw_i,
      dir_out => dir_sync,
      en_out  => en_sync
    );

  -- Eksponer mellomliggende signaler
  duty_cycle <= duty_i;
  dir_raw    <= dir_raw_i;
  en_raw     <= en_raw_i;

end architecture rtl;
