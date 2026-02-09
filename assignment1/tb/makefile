# Makefile

# Simulator and language selection
SIM ?= ghdl
TOPLEVEL_LANG ?= vhdl

# VHDL 2008 (for GHDL)
EXTRA_ARGS +=--std=08

# TOPLEVEL is the name of the toplevel module in your VHDL file
TOPLEVEL = first

VHDL_SOURCES += ../src/$(TOPLEVEL).vhd

#VHDL_SOURCES += $(PWD)/../../hdl/*.vhdl



# create a waveform when running this script
SIM_ARGS +=--wave=$(TOPLEVEL).ghw

# MODULE is the basename of the Python test file
MODULE = tb_$(TOPLEVEL)

# include cocotb's make rules to take care of the simulator setup
include $(shell cocotb-config --makefiles)/Makefile.sim

# To be improved--
# removing generated binary of top entity and .o-file on make clean
#clean::
#-@rm -f $(TOPLEVEL)
#-@rm -f e~$(TOPLEVEL).o
