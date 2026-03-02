# Makefile
# defaults
SIM ?= ghdl
TOPLEVEL_LANG ?= vhdl
# VHDL 2008
EXTRA_ARGS +=--std=08

#--- Oppgave a) bin2ssd ---
#TOPLEVEL = bin2ssd_test
#VHDL_SOURCES += $(PWD)/../src/seg7_pkg.vhd
#VHDL_SOURCES += $(PWD)/../src/bin2ssd_test.vhd
#MODULE = tb_bin2ssd_test

#--- Oppgave b) seg7ctrl ---
#TOPLEVEL = seg7ctrl
#VHDL_SOURCES += $(PWD)/../src/seg7_pkg.vhd
#VHDL_SOURCES += $(PWD)/../src/seg7ctrl_ent.vhd
#VHDL_SOURCES += $(PWD)/../src/seg7ctrl.vhd
#MODULE = tb_seg7ctrl

#--- Oppgave c) self_test_unit ---
#TOPLEVEL = self_test_unit
#VHDL_SOURCES += $(PWD)/../src/self_test_unit.vhd
#MODULE = tb_self_test_unit

#--- Oppgave d) self_test_system ---
TOPLEVEL = self_test_system
VHDL_SOURCES += $(PWD)/../src/seg7_pkg.vhd
VHDL_SOURCES += $(PWD)/../src/seg7ctrl_ent.vhd
VHDL_SOURCES += $(PWD)/../src/seg7ctrl_arch.vhd
VHDL_SOURCES += $(PWD)/../src/self_test_unit.vhd
VHDL_SOURCES += $(PWD)/../src/self_test_system.vhd
MODULE = tb_self_test_system

SIM_ARGS +=--wave=$(TOPLEVEL).ghw

# include cocotb's make rules to take care of the simulator setup
include $(shell cocotb-config --makefiles)/Makefile.sim

# removing generated binary of top entity and .o-file on make clean
clean::
	-@rm -f $(TOPLEVEL)
	-@rm -f e~$(TOPLEVEL).o