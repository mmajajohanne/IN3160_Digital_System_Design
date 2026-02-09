library ieee;
use ieee.std_logic_1164.all;

entity decoder is
    port (
        SW1 : in  std_ulogic;
        SW2 : in  std_ulogic;
        LD1 : out std_ulogic;
        LD2 : out std_ulogic;
        LD3 : out std_ulogic;
        LD4 : out std_ulogic
    );
end entity decoder;