'''
Created on Oct 1, 2012

@author: alendit
'''
from docutils import nodes
from docutils.parsers.rst import directives
from sphinx.util.compat import Directive
from subprocess import call
import os
import sys

try:
    from PIL import Image as IMAGE
except ImportError, error:
    IMAGE = None

# debugging with IPython
#try:
#    from IPython import embed
#except ImportError, e:
#    pass


class UMLGenerateDirective(Directive):
    """UML directive to generate a pyreverse diagram"""
    required_arguments = 1
    optional_arguments = 99
    has_content = False
    DIR_NAME = "uml_images"

    def run(self):
        env = self.state.document.settings.env
        src_dir = env.srcdir
        uml_dir = os.path.join(src_dir, self.DIR_NAME)

        if os.path.basename(uml_dir) not in os.listdir(src_dir):
            os.mkdir(uml_dir)
        env.uml_dir = uml_dir
        os.chdir(uml_dir)

        module_paths = [i for i in self.arguments if not i.startswith('-')]
        cmd_opts = [i for i in self.arguments if i.startswith('-')]
        basename = module_paths[0]
        if '/' in basename:
            basename, _ = os.path.splitext(os.path.basename(basename))

        pyreverse_cmd = os.path.join(os.path.dirname(sys.executable), 'pyreverse')
        if not os.path.exists(pyreverse_cmd):
            pyreverse_cmd = 'pyreverse'
        pyreverse_cmd = [pyreverse_cmd, '-o', 'png']
        if '-p' not in cmd_opts:
            pyreverse_cmd.extend(['-p', basename])
        pyreverse_cmd.extend(cmd_opts)
        pyreverse_cmd.extend([
            (os.path.abspath(os.path.join(src_dir, i)) if '/' in i else i)
            for i in module_paths])
        print "Calling '%s'..." % ' '.join(pyreverse_cmd)
        print call(pyreverse_cmd)
        uri = directives.uri(os.path.join(self.DIR_NAME,
                                          "classes_{0}.png".format(basename)))
        scale = 100
        max_width = 1000
        if IMAGE:
            i = IMAGE.open(os.path.join(src_dir, uri))
            image_width = i.size[0]
            if image_width > max_width:
                scale = max_width * scale / image_width
        img = nodes.image(uri=uri, scale=scale)
        os.chdir(src_dir)
        return [img]


def setup(app):
    """Setup directive"""
    app.add_directive('uml', UMLGenerateDirective)
