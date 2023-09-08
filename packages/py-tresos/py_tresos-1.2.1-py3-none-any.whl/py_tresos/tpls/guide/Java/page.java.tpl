package ${PACKAGE};

import org.eclipse.swt.widgets.Composite;

import dreisoft.tresos.guidedconfig.api.gui.WidgetFactory;
import dreisoft.tresos.guidedconfig.api.gui.form.SWTGroup;
import dreisoft.tresos.guidedconfig.api.gui.page.AbstractPage;

public class ${PAGE_CLASS} extends AbstractPage {

	//
    // defines

    /**
     * The Id of this page.
     */
    public static final String ID = "MyPage";

    /**
     * Widget-Id for the Datetime widget.
     */
    public static final String WIDGETID_DATETIME = "DatatimeWidget";

    /**
     * Widget-Id for the integer.
     */
    public static final String WIDGETID_INT = "IntWidget";

    /**
     * Widget-Id for the string.
     */
    public static final String WIDGETID_STRING = "StringWidget";

    /**
     * Widget-Id for the float.
     */
    public static final String WIDGETID_FLOAT = "FloatWidget";

    /**
     * Widget-Id for the checkbox.
     */
    public static final String WIDGETID_CHECKBOX = "CheckboxWidget";

	public ${PAGE_CLASS}() {
		super();
	}

    @Override
    public String doGetId()
    {
        return ID;
    }

    @Override
    public String doGetTitle()
    {
        //return MyEclipseNLS.TITLE_DEMO_PAGE();
		return "Title";
    }

    @Override
    public String doGetDescription()
    {
        //return MyEclipseNLS.TOOLTIP_DEMO_PAGE();
		return "Description";
    }

    @Override
    protected void doCreateControls(Composite parent)
    {
        // get the widget factory via which all widget are manage and created
        WidgetFactory factory = getWidgetFactory();

        // create a collapseable group
        SWTGroup customGroup = factory.createGroup(parent,
                                                   "GroupWidget1",
                                                   WidgetFactory.GroupDecoration.TITLE,
                                                   WidgetFactory.GroupLayout.VERTICAL,
                                                   "DateTime custom widget");

        //
        // Custom Widget
        // create Custom Datetime widget
        //MyDatetime datetimeWidget = new MyDatetime(WIDGETID_DATETIME, customGroup);
        // create controller for widget to receive events from the wizard engine
        //MyDatetimeController datetimeController = new MyDatetimeController(datetimeWidget, "DatetimeMemento");
        // register controller with the WidgetFactory
        //factory.registerWidgetController(datetimeController);

        //
        // Standard Widgets
        // create a collapseable group
        SWTGroup modelGroup = factory.createGroup(parent,
                                                  "GroupWidget2",
                                                  WidgetFactory.GroupDecoration.TITLE,
                                                  WidgetFactory.GroupLayout.VERTICAL,
                                                  "Data from datamodel");

        // create a checkbox
        factory.createLabel(modelGroup, "LabelWidget1", "LabelMemento1", "boolean");
        factory.createCheckBox(modelGroup, WIDGETID_CHECKBOX, I${COMPONENT}Constants.MEMENTO_CHECKBOX);

        // create spacer
        factory.createSpacer(modelGroup, 2, 1);

        // create a textbox of type integer
        factory.createLabel(modelGroup, "LabelWidget2", "LabelMemento2", "Integer");
        factory.createText(modelGroup, WIDGETID_INT, I${COMPONENT}Constants.MEMENTO_INT, WidgetFactory.TextFormat.INTEGER);

        // create a textbox of type float
        factory.createLabel(modelGroup, "LabelWidget3", "LabelMemento3", "Float");
        factory.createText(modelGroup, WIDGETID_FLOAT, I${COMPONENT}Constants.MEMENTO_FLOAT, WidgetFactory.TextFormat.FLOAT);

        // create a textbox
        factory.createLabel(modelGroup, "LabelWidget4", "LabelMemento4", "Text");
        factory.createText(modelGroup,
                           WIDGETID_STRING,
                           I${COMPONENT}Constants.MEMENTO_STRING,
                           WidgetFactory.TextFormat.TEXT);

        // Layout controls
        factory.layout(parent);
    }
}