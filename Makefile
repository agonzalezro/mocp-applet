BIN=/usr/local/bin/
BONOBO=/usr/lib/bonobo/servers/
APPLET=mocp-applet

all: install

install:
	install -m 0755 $(APPLET).py $(BIN)
	install -m 0644 $(APPLET).server $(BONOBO)

recollect:
	cp $(BIN)$(APPLET).py .
	cp $(BONOBO)$(APPLET).server .

uninstall:
	rm -f $(BIN)$(APPLET).py
	rm -f $(BONOBO)$(APPLET).server
