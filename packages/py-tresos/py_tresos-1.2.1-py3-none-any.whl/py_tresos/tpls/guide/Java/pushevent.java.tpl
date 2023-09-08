package ${PACKAGE};

import java.util.List;

import dreisoft.tresos.datamodel2.api.model.DCtxt;
import dreisoft.tresos.guidedconfig.api.memento.Memento;

import dreisoft.tresos.guidedconfig.api.pushservice.AbstractPushEvent;
import dreisoft.tresos.guidedconfig.api.pushservice.AbstractPushOperation;


public class ${PUSH_EVENT_CLASS} extends AbstractPushEvent {

    //
    // defines

    /**
     * A {@link DCtxt} that references the target configuration that should be altered by the triggered
     * {@link AbstractPushOperation}.
     */
    public static final String VAR_TARGET_CONTEXT = "DContext";

    /**
     * The whole backend of the wizard.
     */
    public static final String VAR_BACKEND = "Backend";

    /**
     * The memento that forms the input to the PusOperation.
     */
    public static final String VAR_MEMENTO = "Memento";

    /**
     * The mementos that have been set from the configuration
     */
    public static final String VAR_CHANGED_MEMENTOS = "ChangedMementos";

	public ${PUSH_EVENT_CLASS}() {
        super();
    }

    /**
     * Set the memento from which to take the data.
     *
     * @param memento The memento of the wizard
     */
    public void setSourceMemento(Memento memento)
    {
        setVariable(VAR_MEMENTO, memento);
    }

    /**
     * Get the root memento of the wizard.
     *
     * @return The memento in the wizard
     */
    public Memento getSourceMemento()
    {
        return (Memento)getVariable(VAR_MEMENTO);
    }

    /**
     * Set the target of the operation.
     *
     * @param target The target
     */
    public void setTargetContext(DCtxt target)
    {
        setVariable(VAR_TARGET_CONTEXT, target);
    }

    /**
     * Get the target of the operation
     *
     * @return The node in the project to change
     */
    public DCtxt getTargetContext()
    {
        return (DCtxt)getVariable(VAR_TARGET_CONTEXT);
    }

    /**
     * Starts a transaction in {@link #getTargetContext()}
     */
    @Override
    protected void doPreOperationsHook()
    {
        super.doPreOperationsHook();
        getTargetContext().startTransaction("Example start operations");
    }

    /**
     * Finishes the transaction started in {@link #doPreOperationsHook()}
     */
    @Override
    protected void doPostOperationsHook()
    {
        super.doPostOperationsHook();
        getTargetContext().finishTransaction();
    }

    /**
     * Set the changed mementos.
     *
     * @param mementos The names of the changed mementos
     */
    public void setChangedMementos(List<String> mementos)
    {
        setVariable(VAR_CHANGED_MEMENTOS, mementos);
    }

    /**
     * Query the list of changed mementos.
     *
     * @return The changed mementos
     */
    @SuppressWarnings("unchecked")
    public List<String> getChangedMementos()
    {
        return (List<String>)getVariable(VAR_CHANGED_MEMENTOS);
    }
}
