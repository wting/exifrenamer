VERSION = v0.2.0

.PHONY: docs install uninstall

install:
	install.sh

uninstall:
	uninstall.sh

docs:
	pandoc -s -w man docs/manpage_header.md docs/header.md docs/manpage.md -o docs/exifrenamer.1
	pandoc -s -w markdown docs/header.md docs/install.md docs/manpage.md -o README.md

release:
	# Check for tag existence
	# git describe release-$(VERSION) 2>&1 >/dev/null || exit 1

	# Create tag
	git tag -s -a $(VERSION)

	# Create tagged archive
	git archive --format=tar --prefix exifrenamer_$(VERSION)/ $(VERSION) | gzip > exifrenamer_$(VERSION).tar.gz
