<?xml version="1.0" encoding="UTF-8"?>
<?eclipse version="3.2"?>
<plugin>
  <extension
        id="#{COMPONENT}XPath"
        point="dreisoft.tresos.datamodel2.api.plugin.xpathregistration">
     <xpathfunction>
        <classregistration
              class="#{JAVA_PACKAGE}.#{JAVA_CLASS}"
              description="This is a custom xpath function for the #{COMPONENT}"
              namespace="#{COMPONENT}">
        </classregistration>
     </xpathfunction>
  </extension>
</plugin>
