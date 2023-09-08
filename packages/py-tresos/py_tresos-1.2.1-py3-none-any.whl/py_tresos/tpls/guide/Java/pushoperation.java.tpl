package ${PACKAGE};

import java.util.ArrayList;
import java.util.List;

import dreisoft.tresos.datamodel2.api.model.DCtxt;

import dreisoft.tresos.guidedconfig.api.pushservice.AbstractPushEvent;
import dreisoft.tresos.guidedconfig.api.memento.Memento;
import dreisoft.tresos.guidedconfig.api.pushservice.AbstractConfigurablePushOperation;


public class ${PUSH_OPERATION_CLASS} extends AbstractConfigurablePushOperation {

    // constants for paths into DCtxt
    public static final String DCTXT_PATH_BOOL = "ExamplesCommon/Bool";
    public static final String DCTXT_PATH_INT = "ExamplesCommon/Int";
    public static final String DCTXT_PATH_STRING = "ExamplesCommon/String";
    public static final String DCTXT_PATH_FLOAT = "ExamplesCommon/Float";

	public ${PUSH_OPERATION_CLASS}() {
        super();
    }

    /**
     * Invokes the push operation.
     *
     * <p>
     * This method does the actual work push transferring data between the
     *
     * @{link AbstractPushEvent} and the project.
     *        </p>
     *
     *        <p>
     *        The demo implementation serves the {@link Demo2Backend}.
     *        </p>
     *
     * @param event The push event
     */
    @Override
    public void doInvoke(AbstractPushEvent event)
    {
        if (!(event instanceof ${PUSH_EVENT_CLASS}))
        {
            return;
        }
        ${PUSH_EVENT_CLASS} eventInstance = (${PUSH_EVENT_CLASS})event;

        // obtain reference to data model from the event for reading data
        DCtxt targetContext = eventInstance.getTargetContext();

        // obtain memento for writing data
        Memento memento = eventInstance.getSourceMemento();

        List<String> changedMemento = new ArrayList<String>();

        // write values from the data model to the memento
        // the data stored in the memento will be used as values of the GUI widget for the dialog
        memento.setBoolean(I${COMPONENT}Constants.MEMENTO_CHECKBOX, targetContext.var.getBool(DCTXT_PATH_BOOL));
        changedMemento.add(I${COMPONENT}Constants.MEMENTO_CHECKBOX);
        memento.setInteger(I${COMPONENT}Constants.MEMENTO_INT, targetContext.var.getInt(DCTXT_PATH_INT));
        changedMemento.add(I${COMPONENT}Constants.MEMENTO_INT);
        memento.setFloat(I${COMPONENT}Constants.MEMENTO_FLOAT, targetContext.var.getFloat(DCTXT_PATH_FLOAT));
        changedMemento.add(I${COMPONENT}Constants.MEMENTO_FLOAT);
        memento.setString(I${COMPONENT}Constants.MEMENTO_STRING, targetContext.var.getString(DCTXT_PATH_STRING));
        changedMemento.add(I${COMPONENT}Constants.MEMENTO_STRING);

        eventInstance.setChangedMementos(changedMemento);
    }
}