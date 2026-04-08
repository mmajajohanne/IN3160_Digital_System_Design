-- quadrature_decoder.vhd
-- FSM som dekoder quadrature-signaler (SA, SB) fra rotary encoder.
-- Genererer pos_inc eller pos_dec pulser (1 klokkeperiode) ved posisjonsendring.

library ieee;
use ieee.std_logic_1164.all;

entity quadrature_decoder is
  port(
    mclk    : in  std_ulogic;
    reset   : in  std_ulogic;
    sa      : in  std_ulogic;
    sb      : in  std_ulogic;
    pos_inc : out std_ulogic;
    pos_dec : out std_ulogic
  );
end entity quadrature_decoder;

architecture rtl of quadrature_decoder is
  type state_type is (s_reset, s_init, s_0, s_1, s_2, s_3);
  signal state, next_state : state_type;
  signal ab : std_ulogic_vector(1 downto 0);

  -- Utgangssignaler fra kombinatorisk logikk
  signal inc_i, dec_i : std_ulogic;
begin

  ab <= sa & sb;

  -- Tilstandsregister + registrerte utganger
  REG : process(mclk) is
  begin
    if rising_edge(mclk) then
      if reset = '1' then
        state   <= s_reset;
        pos_inc <= '0';
        pos_dec <= '0';
      else
        state   <= next_state;
        pos_inc <= inc_i;
        pos_dec <= dec_i;
      end if;
    end if;
  end process REG;

  -- Neste-tilstand og utganger (Mealy: utganger avhenger av state + input)
  COMB : process(all) is
  begin
    -- Standardverdier
    next_state <= state;
    inc_i      <= '0';
    dec_i      <= '0';

    case state is

      when s_reset =>
        -- Gaa alltid til s_init (uansett AB-verdi)
        next_state <= s_init;

      when s_init =>
        -- Hopp til riktig tilstand basert paa AB, ingen inc/dec
        case ab is
          when "00"   => next_state <= s_0;
          when "01"   => next_state <= s_1;
          when "11"   => next_state <= s_2;
          when "10"   => next_state <= s_3;
          when others => next_state <= s_reset;
        end case;

      when s_0 =>  -- AB = 00
        case ab is
          when "00"   => next_state <= s_0;               -- ingen endring
          when "01"   => next_state <= s_1; inc_i <= '1';  -- fremover
          when "11"   => next_state <= s_reset;            -- feil (hoppet over)
          when "10"   => next_state <= s_3; dec_i <= '1';  -- bakover
          when others => next_state <= s_reset;
        end case;

      when s_1 =>  -- AB = 01
        case ab is
          when "00"   => next_state <= s_0; dec_i <= '1';  -- bakover
          when "01"   => next_state <= s_1;                -- ingen endring
          when "11"   => next_state <= s_2; inc_i <= '1';  -- fremover
          when "10"   => next_state <= s_reset;            -- feil
          when others => next_state <= s_reset;
        end case;

      when s_2 =>  -- AB = 11
        case ab is
          when "00"   => next_state <= s_reset;            -- feil
          when "01"   => next_state <= s_1; dec_i <= '1';  -- bakover
          when "11"   => next_state <= s_2;                -- ingen endring
          when "10"   => next_state <= s_3; inc_i <= '1';  -- fremover
          when others => next_state <= s_reset;
        end case;

      when s_3 =>  -- AB = 10
        case ab is
          when "00"   => next_state <= s_0; inc_i <= '1';  -- fremover
          when "01"   => next_state <= s_reset;            -- feil
          when "11"   => next_state <= s_2; dec_i <= '1';  -- bakover
          when "10"   => next_state <= s_3;                -- ingen endring
          when others => next_state <= s_reset;
        end case;

    end case;
  end process COMB;

end architecture rtl;
