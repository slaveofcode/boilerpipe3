import os
import jpype
from os import path

if jpype.isJVMStarted() != True:
    jars = []
    data_dir = path.join(path.dirname(path.realpath(__file__)), 'data')
    for top, dirs, files in os.walk(data_dir):
        for nm in files:       
            jars.append(os.path.join(top, nm))
    jpype.startJVM(jpype.getDefaultJVMPath(), "-Djava.class.path=%s" % os.pathsep.join(jars))

from .extractor import Extractor, EXTRACTORS