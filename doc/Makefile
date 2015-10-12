HTML_PARAMS	= style-html.xsl
MAN_PARAMS	= style-man.xsl

source		= pycrc.xml
targets		= $(source:.xml=.html) $(source:.xml=.1)

all: $(targets)

.PHONY: clean
clean:
	$(RM) $(targets)

.PHONY: check
check:
	xmllint --valid --noout $(source)

%.html: %.xml $(HTML_PARAMS)
	saxon-xslt -o $@ $^

%.1: %.xml $(MAN_PARAMS)
	saxon-xslt -o $@ $^

%.txt: %.html
	links -dump -no-numbering -no-references $< > $@
