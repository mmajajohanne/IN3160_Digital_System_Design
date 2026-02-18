# Makefile
SIM ?= ghdl
TOPLEVEL_LANG ?= vhdl
EXTRA_ARGS += --std=08
TOPLEVEL = pargen

# Oppgave a) og b): automatisk alle filer
#VHDL_SOURCES += $(PWD)/../src/*.vhd

# Oppgave c) og videre:
VHDL_SOURCES += $(PWD)/../src/subprog_pck.vhd
VHDL_SOURCES += $(PWD)/../src/pargen.vhd

SIM_ARGS += --wave=$(TOPLEVEL).ghw 
COCOTB_TEST_MODULES = tb_$(TOPLEVEL)
include $(shell cocotb-config --makefiles)/Makefile.sim
clean::
	-@rm -rf __pycache__
	-@rm -rf sim_build