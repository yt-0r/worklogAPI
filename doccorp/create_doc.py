import base64

from docx.oxml.text.paragraph import CT_P

from docxtpl import DocxTemplate
from docxtpl import Subdoc

import os


# import comtypes.client


class DoccorpTemplate:

    def __init__(self, issue):
        self.doc = DocxTemplate(f"templates/{issue}.docx")
        self.issue = issue

    def my_render(self, render_dict: dict):
        # нужно пройтись по ключам и узнать, есть ли таблицы

        render_table = {}

        for render_key, render_val in render_dict.copy().items():
            if render_key.split('_')[0] == 'table':
                render_dict.pop(render_key)

                subx = self.doc.new_subdoc(f'templates/subs/{render_key}.docx')
                elements = list(subx.element.body)
                if len(elements) > 1 and not isinstance(elements[-2], CT_P):
                    subx.add_paragraph()

                render_dict[render_key] = subx
                render_table[render_key] = render_val

        self.doc.render(render_dict)
        self.doc.save(f'templates/{self.issue}_temp.docx')

        if render_table:
            self.doc = DocxTemplate(f"templates/{self.issue}_temp.docx")
            self.doc.render(render_table)
            self.doc.save(f'templates/{self.issue}_temp.docx')

        if os.name == 'nt':
            from docx2pdf import convert
            convert(f'templates/{self.issue}_temp.docx', f'templates/{self.issue}_temp.pdf')
        if os.name == 'posix':
            import subprocess
            command_uno = ['unoconvert', f'templates/{self.issue}_temp.docx', f'templates/{self.issue}_temp.pdf']
            command = ['libreoffice', '--headless', '--convert-to', 'pdf', '--outdir', 'templates/', f'templates/{self.issue}_temp.docx']
            subprocess.check_output(command)

        # получаем бинарник
        encoded = base64.b64encode(open(f'templates/{self.issue}_temp.pdf', 'rb').read())

        # os.remove(f'templates/{self.issue}_temp.pdf')
        # os.remove(f'templates/{self.issue}_temp.docx')

        return encoded
