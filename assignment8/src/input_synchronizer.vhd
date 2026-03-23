library ieee;
use ieee.std_logic_1164.all;

entity input_synchronizer is
  port(
    mclk  : in  std_ulogic;
    reset : in  std_ulogic;
    -- Asynkrone innganger (fra quadrature encoder)
    sa_in : in  std_ulogic;
    sb_in : in  std_ulogic;
    -- Synkroniserte utganger (til quadrature decoder)
    sa_out : out std_ulogic;
    sb_out : out std_ulogic
  );
end entity input_synchronizer;

architecture rtl of input_synchronizer is
  -- to registre i serie per signal
  signal sa_meta, sa_sync : std_ulogic;
  signal sb_meta, sb_sync : std_ulogic;
begin
  process(mclk) is
  begin
    if rising_edge(mclk) then
      if reset = '1' then
        sa_meta <= '0';
        sa_sync <= '0';
        sb_meta <= '0';
        sb_sync <= '0';
      else
        -- første flipflop fanger asynkront signal (kan bli metastabil)
        sa_meta <= sa_in;
        sb_meta <= sb_in;
        -- andre flipflop gir stabilt synkronisert signal
        sa_sync <= sa_meta;
        sb_sync <= sb_meta;
      end if;
    end if;
  end process;

  sa_out <= sa_sync;
  sb_out <= sb_sync;
end architecture rtl;
