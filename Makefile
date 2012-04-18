PROJ = exifrenamer
VERSION = v0.2.0

.PHONY: docs install uninstall

install:
	mkdir -p ~/.$(PROJ)/bin/
	mkdir -p ~/.$(PROJ)/share/man/man1/
	cp -r ./$(PROJ)/* ~/.$(PROJ)/bin/
	cp ./docs/$(PROJ).1 ~/.$(PROJ)/share/man/man1/

	@echo
	@echo "Add the following line to ~/.bashrc:"
	@echo
	@echo -e "\texport PATH=~/.exifrenamer/bin:\$PATH"
	@echo

uninstall:
	rm -frv ~/.$(PROJ)/

docs:
	pandoc -s -w man docs/manpage_header.md docs/header.md docs/body.md -o docs/$(PROJ).1
	pandoc -s -w markdown docs/header.md docs/install.md docs/body.md -o README.md

release:
	# Create tag
	git tag -s -a $(VERSION)

	# Create tagged archive
	git archive --format=tar --prefix $(PROJ)_$(VERSION)/ $(VERSION) | gzip > $(PROJ)_$(VERSION).tar.gz

clean:
	find -P ./ -type f -name "*.pyc" -exec rm -v {} +
