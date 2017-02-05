dist_noinst_SCRIPTS = xml2po.py

LANGS = ar bg ca cs da de el en en_GB es et fa fi fr fy he hr hu is it ku lt lv nl no nb pl pt pt_BR ro ru sv sk sl sr th tr uk
LANGMO = $(LANGS:=.mo)
LANGPO = $(LANGS:=.po)

EXTRA_DIST = $(LANGPO)

# the TRANSLATORS: allows putting translation comments before the to-be-translated line.
obh-py.pot: $(top_srcdir)/src/*.py
	$(XGETTEXT) --no-wrap -L Python --from-code=UTF-8 --add-comments="TRANSLATORS:" -d @PACKAGE_NAME@ -s -o $@ $^

obh-xml.pot: $(srcdir)/xml2po.py $(top_srcdir)/src/*.xml
	$(PYTHON) $^ > $@

obh.pot: obh-py.pot obh-xml.pot
	sed --in-place obh-py.pot --expression=s/CHARSET/UTF-8/
	sed --in-place obh-xml.pot --expression=s/CHARSET/UTF-8/
	cat $^ | $(MSGUNIQ) --no-wrap --no-location -o $@ -

%.po: obh.pot
	if [ -f $@ ]; then \
		$(MSGMERGE) --backup=none --no-wrap --no-location -s -N -U $@ $< && touch $@; \
	else \
		$(MSGINIT) -l $@ -o $@ -i $< --no-translator; \
	fi

.po.mo:
	$(MSGFMT) -o $@ $<

BUILT_SOURCES = $(LANGMO)
CLEANFILES = $(LANGMO) obh-py.pot obh.pot

dist-hook: $(LANGPO)

install-data-local: $(LANGMO)
	for lang in $(LANGS); do \
		$(mkinstalldirs) $(DESTDIR)/usr/lib/enigma2/python/Plugins/SystemPlugins/OBH/locale/$$lang/LC_MESSAGES; \
		$(INSTALL_DATA) $$lang.po $(DESTDIR)/usr/lib/enigma2/python/Plugins/SystemPlugins/OBH/locale/obh-$$lang.po; \
		$(INSTALL_DATA) $$lang.mo $(DESTDIR)/usr/lib/enigma2/python/Plugins/SystemPlugins/OBH/locale/$$lang/LC_MESSAGES/obh.mo; \
	done

uninstall-local:
	for lang in $(LANGS); do \
		$(RM) $(DESTDIR)/usr/lib/enigma2/python/Plugins/SystemPlugins/OBH/locale/obh-$$lang.po; \
		$(RM) $(DESTDIR)/usr/lib/enigma2/python/Plugins/SystemPlugins/OBH/locale/$$lang/LC_MESSAGES/obh.mo; \
	done
