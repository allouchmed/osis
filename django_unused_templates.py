"""
Django Unused Templates
by Alexander Meng

Generates a list of unused templates in your current directory and subdirectories
by searching all .html and .py files for the names of your templates.

IF YOU OVERRIDE DJANGO TEMPLATES, THEY MAY APPEAR IN THE LIST AS UNUSED.

"""

import os
import sys

MODULES = [
    'all', 'osis', 'internship', 'continuing_education', 'osis_common', 'partnership', 'dissertation', 'assistant'
]
OSIS_MODULES = ['assessments', 'attribution', 'backoffice', 'base', 'cms', 'education_group', 'learning_unit',
                'program_management', 'reference', 'rules_management', 'osis/templates', 'webservices']


def _should_analyze_file(f, submodules, features=False):
    if __is_unconcerned_file(f, features):
        return False
    for folder in submodules:
        if '/' + folder + '/' in f:
            return True
    return False


def __is_unconcerned_file(f, features=False):
    unconcerned_files = ['/venv', '/tests', '/Lib'] + ['/features'] if not features else []
    return all(file in f for file in unconcerned_files)


def _get_files_of_extension(file_extension, filter):
    return [
        f[2:-1]
        for f in os.popen('find . -name "*.' + file_extension + '" | sort').readlines()
        if filter[0](f, **filter[1])
    ]


def _get_templates(html_files):
    # Templates will only be returned if they are located in a
    # /templates/ directory
    template_list = []
    for html_file in html_files:
        if html_file.find("/templates") != 0:
            try:
                template_list.append(html_file.rsplit("templates/")[1])
            except IndexError:
                # The html file is not in a template directory...
                # don't count it as a template
                template_list.append("html")

    return template_list


def get_unused_templates(module_name=None):
    print("Start searching unused templates in module %s" % (module_name if module_name else 'all osis'))
    if not module_name:
        module_name = 'all'
    modules_to_keep = {
        module: (_should_analyze_file, {
            'submodules': OSIS_MODULES if module == 'osis' else MODULES + OSIS_MODULES if module == 'all' else [module]
        })
        for module in MODULES
    }[module_name if module_name else 'osis']
    html_files = _get_files_of_extension('html', modules_to_keep)
    templates = _get_templates(html_files)
    py_files = _get_files_of_extension('py', modules_to_keep)
    files = py_files + html_files  # List of all files
    tl_count = [0 for _ in templates]

    unused_templates = 0
    for file in files:
        f = open(file)
        text = f.read()
        for count, template in enumerate(templates):
            if template in text:
                tl_count[count] = 1
        f.close()

    for count, template in enumerate(templates):
        if tl_count[count] == 0:
            print("Unused template : ", html_files[count])
            unused_templates += 1
    print("\n# Unused templates : ", unused_templates)


def main(argv):
    module = argv[0] if argv else None
    if module and module not in MODULES:
        print("First argument should be a valid module")
        sys.exit()
    get_unused_templates(module)


if __name__ == "__main__":
    main(sys.argv[1:])
