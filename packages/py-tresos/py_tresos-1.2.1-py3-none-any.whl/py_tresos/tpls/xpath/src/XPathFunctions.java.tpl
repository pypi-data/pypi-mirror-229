package ${JAVA_PACKAGE};

import dreisoft.tresos.datamodel2.api.model.DCtxt;
import dreisoft.tresos.datamodel2.api.model.xpath.AbstractXPathFunctions;
import dreisoft.tresos.datamodel2.api.model.xpath.CurrentContext;
import dreisoft.tresos.lib2.api.log.APIInvalidOperationException;


public class ${JAVA_CLASS} extends AbstractXPathFunctions {

	public ${JAVA_CLASS}() {
		super();
	}

	public static Object toDCtxt(CurrentContext context, Object o) throws APIInvalidOperationException {
		DCtxt node = toDCtxt(o);
		String data = node.var.getString();
		return data;
	}
}
