# Makefile

# defaults
SIM ?= ghdl
TOPLEVEL_LANG ?= vhdl

# VHDL 2008 (trengs for process(all) og "and" reduction operator)
EXTRA_ARGS +=--std=08

# TOPLEVEL is the name of the toplevel module in your VHDL file
TOPLEVEL = pdm

VHDL_SOURCES += $(PWD)/../src/pdm.vhd

SIM_ARGS +=--wave=$(TOPLEVEL).ghw

# MODULE is the basename of the Python test file
MODULE = tb_pdm

# include cocotb's make rules to take care of the simulator setup
include $(shell cocotb-config --makefiles)/Makefile.sim

# removing generated binary of top entity and .o-file on make clean
clean::
	-@rm -f $(TOPLEVEL)
	-@rm -f e~$(TOPLEVEL).o