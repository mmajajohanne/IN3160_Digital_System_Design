library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity pulse_width_modulator is
  port(
    mclk, reset : in  std_ulogic;
    duty_cycle  : in  std_ulogic_vector(7 downto 0);
    dir, en     : out std_ulogic
  );
end entity pulse_width_modulator;

architecture rtl of pulse_width_modulator is

  -- Tilstander fra ASM-diagrammet:
  --   idle-tilstandene har EN=0 (motor av), trygt å endre DIR
  --   active-tilstandene har EN=PWM (motor kjører)
  type state_type is (forward_idle, forward, reverse_idle, reverse);
  signal state, next_state : state_type;

  -- duty_cycle tolket som signed for retning og størrelse
  signal duty_signed : signed(7 downto 0);

  -- PDM submodul-signaler
  constant PDM_WIDTH : natural := 20;
  signal setpoint_i  : std_logic_vector(PDM_WIDTH-1 downto 0);
  signal pdm_pulse_i : std_logic;
  signal abs_duty     : unsigned(6 downto 0);

begin

  duty_signed <= signed(duty_cycle);

  -----------------------------------------------------------------
  -- Setpoint-konvertering:
  -- Ta absoluttverdien av duty_cycle (7 bit, 0-127)
  -- og plasser den i MSB av 20-bit setpoint.
  -- Mapper: 0 → 0%, 64 → ~50%, 127 → ~99.2%
  -----------------------------------------------------------------
  abs_duty <= to_unsigned(127, 7)              when duty_signed = -128 else
              unsigned(duty_signed(6 downto 0))  when duty_signed >= 0  else
              unsigned((-duty_signed)(6 downto 0));

  setpoint_i <= std_logic_vector(abs_duty) & "0000000000000";

  -----------------------------------------------------------------
  -- PDM submodul: genererer selve pulsmønsteret
  -- mea_req bundet til '0' (ikke brukt i denne applikasjonen)
  -- Konstanter fra oppgaven sikrer trygg PWM-frekvens (< 7 kHz)
  -----------------------------------------------------------------
  pdm_inst : entity work.pdm
    generic map(WIDTH => PDM_WIDTH)
    port map(
      clk       => mclk,
      reset     => reset,
      mea_req   => '0',
      setpoint  => setpoint_i,
      min_off   => x"000FF",
      min_on    => x"00FF0",
      max_on    => x"FFF00",
      mea_ack   => open,
      pdm_pulse => pdm_pulse_i
    );

  -----------------------------------------------------------------
  -- Tilstandsregister med synkron reset
  -- Reset → reverse_idle (EN=0, DIR=0), trygg starttilstand
  -----------------------------------------------------------------
  REG : process(mclk) is
  begin
    if rising_edge(mclk) then
      if reset = '1' then
        state <= reverse_idle;
      else
        state <= next_state;
      end if;
    end if;
  end process REG;

  -----------------------------------------------------------------
  -- Neste-tilstand-logikk (kombinatorisk)
  --
  -- Sikkerhetsprinsipp: retningsskifte går alltid gjennom
  -- en idle-tilstand, slik at EN=0 i minst én klokkesyklus
  -- før DIR endres.
  --
  -- Flyt ved retningsskifte:
  --   forward → forward_idle → reverse_idle → reverse
  --   reverse → reverse_idle → forward_idle → forward
  -----------------------------------------------------------------
  NEXT_STATE_CL : process(all) is
  begin
    next_state <= state; -- default: bli i nåværende tilstand

    case state is
      when reverse_idle =>
        if duty_signed < 0 then
          next_state <= reverse;
        elsif duty_signed > 0 then
          next_state <= forward_idle;
        end if;

      when reverse =>
        if duty_signed >= 0 then
          next_state <= reverse_idle;
        end if;

      when forward_idle =>
        if duty_signed > 0 then
          next_state <= forward;
        elsif duty_signed < 0 then
          next_state <= reverse_idle;
        end if;

      when forward =>
        if duty_signed <= 0 then
          next_state <= forward_idle;
        end if;
    end case;
  end process NEXT_STATE_CL;

  -----------------------------------------------------------------
  -- Moore utgangslogikk (kombinatorisk fra tilstand)
  -- Ingen ekstra registre — dekodes direkte fra tilstand,
  -- slik testbenken anbefaler.
  -----------------------------------------------------------------
  dir <= '1' when state = forward or state = forward_idle else '0';
  en  <= pdm_pulse_i when state = forward or state = reverse else '0';

end architecture rtl;
