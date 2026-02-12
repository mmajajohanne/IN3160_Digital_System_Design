library ieee;
use ieee.std_logic_1164.all;

entity shiftn is
  generic (
    N : positive := 8
  );
  port (
    rst_n      : in  std_ulogic;
    mclk       : in  std_ulogic;
    serial_in  : in  std_ulogic;
    q          : out std_ulogic_vector(N-1 downto 0);
    serial_out : out std_ulogic
  );
end entity shiftn;

------------------------------------
architecture structural of shiftn is

  component dff is
    port (
      rst_n : in  std_ulogic;
      mclk  : in  std_ulogic;
      din   : in  std_ulogic;
      dout  : out std_ulogic
    );
  end component;

  signal q_int : std_ulogic_vector(N-1 downto 0);

begin


  q <= q_int;
  serial_out <= q_int(0);

	-- MSB (første flipflop som får serial_in direkte)
  DFF_MSB : dff
    port map (
      rst_n => rst_n,
      mclk  => mclk,
      din   => serial_in,
      dout  => q_int(N-1)
    );
	
	-- gjenværende biter med generate
  gen_shift : for i in N-2 downto 0 generate

    DFF_i : dff
      port map (
        rst_n => rst_n,
        mclk  => mclk,
        din   => q_int(i+1),
        dout  => q_int(i)
      );

  end generate;

end architecture structural;