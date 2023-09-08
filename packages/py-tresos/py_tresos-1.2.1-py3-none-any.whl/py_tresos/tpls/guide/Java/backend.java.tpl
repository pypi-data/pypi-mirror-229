package ${PACKAGE};

import java.util.List;

import dreisoft.tresos.datamodel2.api.model.DCtxt;
import dreisoft.tresos.guidedconfig.api.backend.AbstractBackend;
import dreisoft.tresos.guidedconfig.api.context.ECUConfigContext;
import dreisoft.tresos.guidedconfig.api.gui.page.AbstractPage;
import dreisoft.tresos.guidedconfig.api.pushservice.PushService;

public class ${BACKEND_CLASS} extends AbstractBackend {

	/**
     * Path to the MODULE-DEF of the demo module
     */
    public static final String MODULE_SCHEMA_PATH = "/AUTOSAR/TOP-LEVEL-PACKAGES/TS_T00D0M0I0R0/ELEMENTS/GCDemo2";

	public ${BACKEND_CLASS}() {
		super();
	}

    @Override
    public void doShowPage(AbstractPage page)
    {
        // let a PushOperation fill part of the mementos of this wizard
        // the widgets filled from the datamodel are disabled, as we do not
        // send these data back to the datamodel while finishing

        ${PUSH_EVENT_CLASS} event = new ${PUSH_EVENT_CLASS}();
        event.setSourceMemento(getMemento());
        DCtxt targetConfigurationContext = getTargetConfigurationContext(MODULE_SCHEMA_PATH);
        if (targetConfigurationContext == null)
        {
            throw new IllegalArgumentException(
                "Cannot retrieve data context from path " + MODULE_SCHEMA_PATH);
        }
        event.setTargetContext(targetConfigurationContext);

        // Trigger PushOperations
        PushService.getInstance().callSync(event, false);
    }

    @Override
    public void doUpdateWidgetEnablement()
    {
        // disable all widgets in the datamodel group as the values may not be changed
        changeWidgetEnablement(${PAGE_CLASS}.WIDGETID_CHECKBOX, false);
        changeWidgetEnablement(${PAGE_CLASS}.WIDGETID_INT, false);
        changeWidgetEnablement(${PAGE_CLASS}.WIDGETID_STRING, false);
        changeWidgetEnablement(${PAGE_CLASS}.WIDGETID_FLOAT, false);
    }

    /**
     * Get the first configuration node of the project configuration to which this wizard belongs which matches the
     * given path in the schema (parameter definition).
     *
     * @param schemaPath The schema path
     * @return The referenced configuration node or null
     */
    public DCtxt getTargetConfigurationContext(String schemaPath)
    {
        ECUConfigContext ecuConfigContext = (ECUConfigContext)getContexts().get(ECUConfigContext.ID);
        List<DCtxt> dctxts = ecuConfigContext.getDCtxt().getFromSchema(schemaPath);
        return (dctxts != null) && (dctxts.size() > 0) ? dctxts.get(0) : null;
    }
}
