library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity pdm is
    generic (WIDTH : natural := 16);
    port (
        clk, reset, mea_req : in  std_logic;
        setpoint, min_off,
        min_on, max_on      : in  std_logic_vector(WIDTH-1 downto 0);
        mea_ack, pdm_pulse  : out std_logic
    );
end entity pdm;

architecture rtl of pdm is

    -- tilstander fra ASMD-diagrammet
    type state_type is (s_low, s_high, s_mea);
    signal state, next_state : state_type;

    -- akkumulator (WIDTH+1 bit, MSB = PDM_out)
    signal r_acc, next_acc : unsigned(WIDTH downto 0) := (others => '0');
    alias PDM_out : std_logic is r_acc(r_acc'left);

    -- timer og counter
    signal timer, next_timer   : unsigned(WIDTH-1 downto 0) := (others => '0');
    signal counter, next_counter : unsigned(WIDTH-1 downto 0) := (others => '0');

begin

    -- akkumulator-addisjon (fra oppgave a, kjører alltid)
    next_acc <= ('0' & unsigned(setpoint)) + ('0' & r_acc(WIDTH-1 downto 0));

    -- registerprosess: én prosess for alle registre
    -- synkron reset
    REG : process(clk) is
    begin
        if rising_edge(clk) then
            if reset = '1' then
                state   <= s_low;
                r_acc   <= (others => '0');
                timer   <= (others => '0');
                counter <= (others => '0');
            else
                state   <= next_state;
                r_acc   <= next_acc;
                timer   <= next_timer;
                counter <= next_counter;
            end if;
        end if;
    end process REG;

    -- next-state logikk (kombinatorisk)
    NEXT_STATE_CL : process(all) is
    begin
        next_state <= state; -- default: bli i nåværende tilstand

        case state is
            when s_low =>
                if mea_req = '1' then
                    next_state <= s_mea;
                elsif timer = 0 and counter >= unsigned(min_on) then
                    next_state <= s_high;
                end if;

            when s_high =>
                if timer = 0 or counter = 0 then
                    -- sjekk mea_req ved utgang (fra ASMD-diagrammet)
                    if mea_req = '1' then
                        next_state <= s_mea;
                    else
                        next_state <= s_low;
                    end if;
                end if;

            when s_mea =>
                if mea_req = '0' then
                    next_state <= s_low;
                end if;
        end case;
    end process NEXT_STATE_CL;

  
    -- output- og next-value logikk (kombinatorisk)
    OUTPUT_CL : process(all) is
    begin
        -- defaults (fra ASMD-diagrammet)
        pdm_pulse    <= '0';
        mea_ack      <= '0';
        next_timer   <= timer - 1 when timer > 0 else (others => '0');
        next_counter <= counter;

        case state is
            when s_low =>
                -- overgang til s_high: last timer med max_on
                if timer = 0 and counter >= unsigned(min_on) and mea_req = '0' then
                    next_timer <= unsigned(max_on);
                end if;

                -- counter teller opp når PDM_out = '1' og når vi ikke går til s_high
                if PDM_out = '1' and (and counter) = '0'
                   and not (timer = 0 and counter >= unsigned(min_on)) then
                    next_counter <= counter + 1;
                end if;

            when s_high =>
                pdm_pulse <= '1';

                -- overgang ut: last timer med min_off
                if timer = 0 or counter = 0 then
                    next_timer <= unsigned(min_off);
                end if;

                -- counter teller ned når PDM_out = '0'
                if PDM_out = '0' and counter > 0 then
                    next_counter <= counter - 1;
                end if;

            when s_mea =>
                mea_ack <= '1';

        end case;
    end process OUTPUT_CL;

end architecture rtl;