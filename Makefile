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

release: docs
	@echo
	@echo "Update and commit ChangeLog, hit <ENTER> to continue..."
	@echo
	@read

	# Check for tag existence
	git describe --tags $(VERSION) 2>&1 >/dev/null && exit 1

	# Modify exifrenamer with correct version
	sed -i "s/^VERSION = \".*\"/VERSION = \"$(VERSION)\"/" ./$(PROJ)/$(PROJ)

	# Commit the version change
	git commit -m "version numbering" ./$(PROJ)/$(PROJ)

	# Create tag
	git tag -s -a $(VERSION)

	# Create tagged archive
	git archive --format=tar --prefix $(PROJ)_$(VERSION)/ $(VERSION) | gzip > $(PROJ)_$(VERSION).tar.gz

clean:
	find -P ./ -type f -name "*.pyc" -exec rm -v {} +
