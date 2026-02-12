library ieee;
use ieee.std_logic_1164.all;

entity shift8 is
	port (
		rst_n : in std_ulogic;
		mclk : in std_ulogic;
		serial_in : in std_ulogic;
		q : out std_ulogic_vector(7 downto 0);
		serial_out : out std_ulogic
	);
end entity shift8;


-------------------------------------------
architecture structural of shift8 is
	signal q_int : std_ulogic_vector(7 downto 0);
	
-- deklarasjon: "dette er komponenten og portene som skal brukes"
	component dff is
		port (
			rst_n : in std_ulogic;
			mclk : in std_ulogic;
			din : in std_ulogic;
			dout : out std_ulogic
		);
	end component;


begin
	q <= q_int; -- parallel output
	
	serial_out <= q_int(0); -- serial output (fra siste del)
	
	--- del 7 får serial_in
	DFF7 : dff
		port map (
			rst_n => rst_n,
			mclk => mclk,
			din => serial_in,
			dout => q_int(7)
		);
	
	-- gjenværende deler skifter til høyre: q_int(i) mater q_int(i-1)
	DFF6 : dff
    port map (
      rst_n => rst_n,
      mclk  => mclk,
      din   => q_int(7),
      dout  => q_int(6)
    );

  DFF5 : dff
    port map (
      rst_n => rst_n,
      mclk  => mclk,
      din   => q_int(6),
      dout  => q_int(5)
    );

  DFF4 : dff
    port map (
      rst_n => rst_n,
      mclk  => mclk,
      din   => q_int(5),
      dout  => q_int(4)
    );

  DFF3 : dff
    port map (
      rst_n => rst_n,
      mclk  => mclk,
      din   => q_int(4),
      dout  => q_int(3)
    );

  DFF2 : dff
    port map (
      rst_n => rst_n,
      mclk  => mclk,
      din   => q_int(3),
      dout  => q_int(2)
    );

  DFF1 : dff
    port map (
      rst_n => rst_n,
      mclk  => mclk,
      din   => q_int(2),
      dout  => q_int(1)
    );

  DFF0 : dff
    port map (
      rst_n => rst_n,
      mclk  => mclk,
      din   => q_int(1),
      dout  => q_int(0)
    );

end architecture structural;