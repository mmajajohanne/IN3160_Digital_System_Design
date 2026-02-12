SIM ?= ghdl
TOPLEVEL_LANG ?= vhdl
EXTRA_ARGS += --std=08

# -------- oppgave A (8-bit) --------
# TOPLEVEL := shift8
# MODULE := tb_shift8
# VHDL_SOURCES += $(PWD)/../src/shift8.vhd

# -------- oppgave B (32-bit) --------
# TOPLEVEL := shift32
# MODULE := tb_shift32
# VHDL_SOURCES += $(PWD)/../src/shift32.vhd
# SIM_ARGS += -gWIDTH=32

# -------- oppgave C (n-bit, 64-bit test) --------
TOPLEVEL := shiftn
MODULE := tb_shiftn
VHDL_SOURCES += $(PWD)/../src/shiftn.vhd
SIM_ARGS += -gN=64

# common file
VHDL_SOURCES += $(PWD)/../src/dff.vhd

SIM_ARGS += --wave=$(TOPLEVEL).ghw

include $(shell cocotb-config --makefiles)/Makefile.sim

clean::
	-@rm -f *.ghw