#!/usr/local/brion_AVX/python/2.7.17_1/bin/python

#import jinja2
import imp
import os
import sys

def import_file(full_path_to_module):
    try:
        module_dir, module_file = os.path.split(full_path_to_module)
        module_name, module_ext = os.path.splitext(module_file)
        save_cwd = os.getcwd()
        os.chdir(module_dir)
        module_obj = __import__(module_name)
        module_obj.__file__ = full_path_to_module
        globals()[module_name] = module_obj
        os.chdir(save_cwd)
    except:
        raise ImportError
#import_file('/home/somebody/somemodule.py')

def import_package_from(modName, modDirPath):
  try:
    sys.path.insert(0, '')
    cwdSave = os.getcwd()
    os.chdir(modDirPath)
    print("CWD: %s" % os.getcwd())
    moduleObj = __import__(modName)
    print("moduleObj.__path__ = %r" % moduleObj.__path__)
    moduleObj.__path__ = [os.path.join(modDirPath, moduleObj.__path__[0])]
    moduleObj.__file__ = os.path.join(modDirPath, moduleObj.__file__)
    globals()[modName] = moduleObj
    sys.path.pop(0)
    os.chdir(cwdSave)
    return moduleObj
  except ImportError as impx:
    raise impx
#import_package_from("modul-name", "path-dir containing-pkg-dir")



if __name__ == "__main__":
  print("sys.path: %s\n" % repr(sys.path))

#  status = imp.load_source("jinja2", "/usr/local/brion_AVX/python/2.7.5_23/lib/python2.7/site-packages/IPython/html/static/components/codemirror/mode/jinja2")

#  print("status = %r" % status)
#  print("jinja2.__version__ = %r" % jinja2.__version__)

  modObj = import_package_from("jinja2", "/usr/local/brion_AVX/python/2.7.5_23/lib/python2.7/site-packages")
  print("modObj.__version__ = %r" % modObj.__version__)
  print("modObj.__path__ = %r" % modObj.__path__)
  print("modObj.__file__ = %r" % modObj.__file__)
  print("globals()['jinja2'] = %s" % globals()["jinja2"])
  print("jinja2.__version__ = %r" % jinja2.__version__)

