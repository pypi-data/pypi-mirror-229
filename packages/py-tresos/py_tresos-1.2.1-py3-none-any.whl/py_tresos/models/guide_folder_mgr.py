import os
import os.path

from shutil import copyfile
from string import Template

from .abstract_folder_mgr import Templatelternative
from .guide_info import GuideInfo


def _copy_file(src, dst):
    root_path = os.path.abspath(__file__ + '/../../tpls/guide')
    copyfile(os.path.realpath(root_path + "/" + src), dst)


def _generate_config_file(src, dst, info: GuideInfo, delimiter="#"):
    if os.path.exists(dst):
        print("<%s> exists and skipped" % dst)
        return

    print("Generate <%s>" % dst)

    root_path = os.path.abspath(__file__ + '/../../tpls/guide')

    with open(root_path + "/" + src) as f_in:
        content = f_in.read()

    if delimiter == "#":
        t = Templatelternative(content)
    else:
        t = Template(content)
    #if (date_time == ""):
    #    new_content = t.substitute(COMPONENT=component, VERSION=version)
    #else:
    new_content = t.substitute(
        COMPONENT = info.name, 
        VERSION = info.eb_version, 
        YEAR = info.year,
        AUTHOR = info.author,
        COMPANY = info.company,
        MAJOR = info.major, 
        MINOR = info.minor,
        PATCH = info.patch,
        AR_MAJOR = info.ar_major,
        AR_MINOR = info.ar_minor,
        AR_PATCH = info.ar_patch,
        AR_PACKAGE = info.ar_package,
        DATE_TIME = info.date_time, 
        PACKAGE = info.package,
        TRESOS_ROOT = info.tresos_root, 
        BACKEND_CLASS = info.backend_class,
        PAGE_CLASS = info.page_class,
        PUSH_EVENT_CLASS = info.push_event_class,
        PUSH_OPERATION_CLASS = info.push_operation_class,
        SIDEBAR_CATEGORY = info.sidebar_category,
        SIDEBAR_LABEL = info.sidebar_label,
        SIDEBAR_TOOLTIP = info.sidebar_tooltip
    )

    with open(dst, 'w') as f_out:
        f_out.write(new_content)

def _generate_plugin_file(src, dst, info: GuideInfo):
    if os.path.exists(dst):
        print("<%s> exists and skipped" % dst)
        return

    print("Generate <%s>" % dst)

    root_path = os.path.abspath(__file__ + '/../../tpls/guide')

    with open(root_path + "/" + src) as f_in:
        content = f_in.read()

    t = Templatelternative(content)

    new_content = t.substitute(
        COMPONENT = info.name, 
        VERSION = info.eb_version, 
        YEAR = info.year,
        AUTHOR = info.author,
        COMPANY = info.company,
        MAJOR = info.major, 
        MINOR = info.minor,
        PATCH = info.patch,
        AR_MAJOR = info.ar_major,
        AR_MINOR = info.ar_minor,
        AR_PATCH = info.ar_patch,
        AR_PACKAGE = info.ar_package,
        PACKAGE = info.package,
        BACKEND_CLASS = info.backend_class,
        PAGE_CLASS = info.page_class,
        PUSH_EVENT_CLASS = info.push_event_class,
        PUSH_OPERATION_CLASS = info.push_operation_class,
        SIDEBAR_CATEGORY = info.sidebar_category,
        SIDEBAR_LABEL = info.sidebar_label,
        SIDEBAR_TOOLTIP = info.sidebar_tooltip
    )

    with open(dst, 'w') as f_out:
        f_out.write(new_content)


def eb_guide_create(cfg_file):

    info = GuideInfo()
    info.parse(cfg_file)

    print("Generate %s (%d.%d.%d)" % (info.name, info.major, info.minor, info.patch))

    create_folders(root_path = info.root_path)

    _generate_plugin_file('plugin.xml.tpl', '%s/plugin.xml' % info.root_path, info = info)

    #_generate_config_file('doc/user_manual.md', '%s/doc/%s_um.md' % (info.root_path, info.name), info = info, delimiter='$')
    _generate_config_file('config/template.xdm.tpl', '%s/config/%s.xdm' % (info.root_path, info.name), info = info)

    _generate_config_file('.project.tpl', '%s/.project' % info.root_path, info = info)
    _generate_config_file("META-INF/MANIFEST.MF.tpl", '%s/META-INF/MANIFEST.MF' % info.root_path,  info = info)
    _generate_config_file("component.ant.tpl",'%s/%s.ant' % (info.root_path, info.name),  info = info)

    # generate the java source 
    java_path = os.path.join(info.root_path, "Java", info.package_path)

    os.makedirs(java_path, exist_ok=True)
    _generate_config_file('Java/backend.java.tpl', '%s/%s' % (java_path, info.backend_class + ".java"), info = info, delimiter='$')
    _generate_config_file('Java/page.java.tpl', '%s/%s' % (java_path, info.page_class + ".java"), info = info, delimiter='$')
    _generate_config_file('Java/constants.java.tpl', '%s/%s' % (java_path, "I" + info.name + "Constants.java"), info = info, delimiter='$')
    if (info.push_event_class != ""):
        _generate_config_file('Java/pushevent.java.tpl', '%s/%s' % (java_path, info.push_event_class + ".java"), info = info, delimiter='$')
    if (info.push_operation_class != ""):
        _generate_config_file('Java/pushoperation.java.tpl', '%s/%s' % (java_path, info.push_operation_class + ".java"), info = info, delimiter='$')

    _copy_file(".classpath.tpl", '%s/.classpath' % info.root_path)
    _copy_file("build.properties.tpl", '%s/build.properties' % info.root_path)


def create_folders(root_path):
    os.makedirs(root_path, exist_ok=True)
    os.makedirs(root_path + "/config", exist_ok=True)
    os.makedirs(root_path + "/META-INF", exist_ok=True)
    os.makedirs(root_path + "/doc", exist_ok=True)
    os.makedirs(root_path + "/src", exist_ok=True)
