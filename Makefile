###############################################################################
MK_INFO := https://pypi.org/project/vmklib
ifeq (,$(shell which mk))
$(warning "No 'mk' in $(PATH), install 'vmklib' with 'pip' ($(MK_INFO))")
endif
ifndef MK_AUTO
$(error target this Makefile with 'mk', not '$(MAKE)' ($(MK_INFO)))
endif
###############################################################################

.PHONY: all edit clean s

.DEFAULT_GOAL := all

all: $(DZ_PREFIX)sync yaml

edit: $(PY_PREFIX)edit

clean: $(PY_PREFIX)clean $(DZ_PREFIX)clean

s:
	./venv$(PYTHON_VERSION)/bin/runtimepy arbiter ./local/arbiter/test.yaml
