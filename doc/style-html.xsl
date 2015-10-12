<?xml version='1.0'?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
<xsl:import href="file:///usr/share/xml/docbook/stylesheet/docbook-xsl-ns/xhtml5/docbook.xsl"/>

<xsl:output encoding="UTF-8" indent="no" method="html"/>
<xsl:param name="default.table.frame"   select="none"/>
<xsl:param name="html.cleanup"          select="1"/>
<xsl:param name="make.valid.html"       select="1"/>

<xsl:template name="user.head.content">
    <meta name="viewport" content="width=device-width, initial-scale=1"/>
</xsl:template>

</xsl:stylesheet>
