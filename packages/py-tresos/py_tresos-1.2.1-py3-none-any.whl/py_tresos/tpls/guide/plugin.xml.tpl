<?xml version="1.0" encoding="UTF-8"?>
<?eclipse version="3.2"?>
<plugin>
  <!--
    Standard module definition extension point
  -->
  <extension point="dreisoft.tresos.launcher2.plugin.module"
             id="#{COMPONENT}_TS_#{VERSION}"
             name="#{COMPONENT}_TS_#{VERSION} Module">

    <module id="#{COMPONENT}_TS_#{VERSION}"
            label="#{COMPONENT}"
            mandatory="false"
            allowMultiple="false"
            description="ECU Information"
            copyright="(c) #{YEAR} #{COMPANY}"
            swVersionMajor="#{MAJOR}"
            swVersionMinor="#{MINOR}"
            swVersionPatch="#{PATCH}"
            specVersionMajor="4"
            specVersionMinor="0"
            specVersionPatch="0"
            specVersionSuffix="0000"
            relVersionMajor="#{AR_MAJOR}"
            relVersionMinor="#{AR_MINOR}"
            relVersionPatch="#{AR_PATCH}"
            categoryType="#{COMPONENT}"
            categoryLayer="Drivers"
            categoryCategory="ECU Firmware"
            categoryComponent="ECUC">
    </module>
   </extension>

   <!--
    extension point defining the schema and data structure of the module
   -->
    <extension point="dreisoft.tresos.launcher2.plugin.configuration"
             id="#{COMPONENT}_TS_#{VERSION}_ConfigId"
             name="#{COMPONENT}_TS_#{VERSION} Configuration">
    <configuration moduleId="#{COMPONENT}_TS_#{VERSION}">

         <!-- schema definition -->
           <schema>
               <manager class="dreisoft.tresos.autosar2.resourcehandling.AutosarSchemaManager"/>
               <resource value="config/#{COMPONENT}.xdm" type="xdm"/>
           </schema>

           <!-- data definition -->
           <data>
               <manager class="dreisoft.tresos.autosar2.resourcehandling.AutosarConfigManager"/>
               <schemaNode path="ASPath:/#{AR_PACKAGE}/#{COMPONENT}"/>
           </data>

           <!-- generic editor definition -->
           <editor id="#{COMPONENT}_TS_#{VERSION}_Editor"
                   label="Default"
                   tooltip="Editor for the #{COMPONENT}_TS_#{VERSION}_Editor module">
               <class class="dreisoft.tresos.launcher2.editor.GenericConfigEditor">
                 <parameter name="schema" value="ASPath:/#{AR_PACKAGE}/#{COMPONENT}"/>
                 <parameter name="title" value="#{COMPONENT}_TS_#{VERSION}_Editor editor"/>
               </class>
           </editor>
       </configuration>
   </extension>

   <extension point="dreisoft.tresos.guidedconfig.api.plugin.guidedconfigwizard">
      <guidedconfigwizard id="#{COMPONENT}">
         <backend class="#{PACKAGE}.#{BACKEND_CLASS}"/>
         <gui class="#{PACKAGE}.#{PAGE_CLASS}"/>
         <resultGui
            class="dreisoft.tresos.guidedconfig.api.gui.page.ChangedDCtxtsResultWidget"
            plugin="dreisoft.tresos.guidedconfig.api.plugin">
         </resultGui>
      </guidedconfigwizard>
   </extension>

   <extension point="dreisoft.tresos.guidedconfig.api.plugin.trigger">
      <trigger>
         <sidebar
              categoryId="#{SIDEBAR_CATEGORY}" 
              id="#{COMPONENT}"
              type="GCDemo"
              wizardId="#{COMPONENT}"
              wizardType="editor">
            <visibility>
               <with variable="ECUConfigContext.moduleId.#{COMPONENT}_TS_#{VERSION}">
                  <equals value="true"/>
               </with>
            </visibility>
            <display
                 label="#{SIDEBAR_LABEL}"
                 tooltip="#{SIDEBAR_TOOLTIP}">
            </display>
         </sidebar>
      </trigger>
   </extension>

   <extension point="dreisoft.tresos.guidedconfig.api.plugin.pushservice">
      <pushoperation
           desc="#{COMPONENT} Push Operation"
           id="#{COMPONENT}PushOperation"
           name="#{COMPONENT} Pull Operation">
         <operationclass
            class="#{PACKAGE}.#{PUSH_OPERATION_CLASS}">
         </operationclass>
         <event>
            <with variable="class">
               <equals value="#{PACKAGE}.#{PUSH_EVENT_CLASS}"/>
            </with>
         </event>
      </pushoperation>
   </extension>

</plugin>
