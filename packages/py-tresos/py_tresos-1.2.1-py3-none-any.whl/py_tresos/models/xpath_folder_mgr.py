import os
import os.path

from shutil import copyfile
from string import Template

from .abstract_folder_mgr import Templatelternative
from .xpath_info import XPathInfo


def _copy_file(src, dst):
    root_path = os.path.abspath(__file__ + '/../../tpls/xpath')
    copyfile(os.path.realpath(root_path + "/" + src), dst)


def _generate_config_file(src, dst, info: XPathInfo, delimiter="#"):
    if os.path.exists(dst):
        print("<%s> exists and skipped" % dst)
        return

    print("Generate <%s>" % dst)

    root_path = os.path.abspath(__file__ + '/../../tpls/xpath')

    with open(root_path + "/" + src) as f_in:
        content = f_in.read()

    if delimiter == "#":
        t = Templatelternative(content)
    else:
        t = Template(content)
    # if (date_time == ""):
    #    new_content = t.substitute(COMPONENT=component, VERSION=version)
    # else:
    new_content = t.substitute(
        COMPONENT=info.name,
        VERSION=info.eb_version,
        YEAR=info.year,
        AUTHOR=info.author,
        COMPANY=info.company,
        MAJOR=info.major,
        MINOR=info.minor,
        PATCH=info.patch,
        AR_MAJOR=info.ar_major,
        AR_MINOR=info.ar_minor,
        AR_PATCH=info.ar_patch,
        DATE_TIME=info.date_time,
        JAVA_PACKAGE=info.java_package,
        JAVA_CLASS=info.java_class
    )

    with open(dst, 'w') as f_out:
        f_out.write(new_content)


def _generate_plugin_file(src, dst, info: XPathInfo):
    if os.path.exists(dst):
        print("<%s> exists and skipped" % dst)
        return

    print("Generate <%s>" % dst)

    root_path = os.path.abspath(__file__ + '/../../tpls/xpath')

    with open(root_path + "/" + src) as f_in:
        content = f_in.read()

    t = Templatelternative(content)
    new_content = t.substitute(
        COMPONENT=info.name,
        VERSION=info.eb_version,
        YEAR=info.year,
        AUTHOR=info.author,
        COMPANY=info.company,
        MAJOR=info.major,
        MINOR=info.minor,
        PATCH=info.patch,
        AR_MAJOR=info.ar_major,
        AR_MINOR=info.ar_minor,
        AR_PATCH=info.ar_patch,
        JAVA_PACKAGE=info.java_package,
        JAVA_CLASS=info.java_class
    )

    with open(dst, 'w') as f_out:
        f_out.write(new_content)


def eb_xpath_create(cfg_file):

    info = XPathInfo()
    info.parse(cfg_file)

    print("Generate %sXPath (%d.%d.%d)" %
          (info.name, info.major, info.minor, info.patch))

    create_folders(root_path=info.root_path)

    _generate_plugin_file('plugin.xml.tpl', '%s/plugin.xml' %
                          info.root_path, info=info)

    _generate_config_file('.project.tpl', '%s/.project' %
                          info.root_path, info=info)
    _generate_config_file("META-INF/MANIFEST.MF.tpl",
                          '%s/META-INF/MANIFEST.MF' % info.root_path,  info=info)
    #_generate_config_file("component.ant.tpl",'%s/%s.ant' % (info.root_path, info.name),  info = info)

    src_path = os.path.join(info.root_path, "src", info.java_package_path)

    os.makedirs(src_path, exist_ok=True)
    _generate_config_file('src/XPathFunctions.java.tpl', '%s/%s' %
                          (src_path, info.java_class + ".java"), info=info, delimiter='$')

    _copy_file(".classpath.tpl", '%s/.classpath' % info.root_path)
    _copy_file("build.properties.tpl", '%s/build.properties' % info.root_path)


def create_folders(root_path):
    os.makedirs(root_path, exist_ok=True)
    os.makedirs(root_path + "/src", exist_ok=True)
    os.makedirs(root_path + "/META-INF", exist_ok=True)
    #os.makedirs(root_path + "/doc", exist_ok=True)
