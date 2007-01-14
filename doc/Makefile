XSLTPROC		= xsltproc
XSLTPARAM		= --nonet --novalid
HTML_STYLESHEET	= /usr/share/xml/docbook/stylesheet/nwalsh/xhtml/docbook.xsl
MAN_STYLESHEET	= /usr/share/xml/docbook/stylesheet/nwalsh/manpages/docbook.xsl

TARGETS		= pycrc.html pycrc.1 faq.html faq.txt

all: $(TARGETS)

.PHONY: clean
clean:
	$(RM) $(TARGETS)

%.html: %.xml
	$(XSLTPROC) $(XSLTPARAM) -o $@ $(HTML_STYLESHEET) $<

%.1: %.xml
	$(XSLTPROC) $(XSLTPARAM) -o $@ $(MAN_STYLESHEET) $<

%.txt: %.html
	links -dump -no-numbering -no-references $< > $@
