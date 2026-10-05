.PHONY: run-ugm
run-ugm: $(INSTALL_TARGETS)
	@$(VENV_FOLDER)/bin/pserve cfg/ugm.ini
