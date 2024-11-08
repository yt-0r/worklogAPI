import base64
from docx.oxml.text.paragraph import CT_P
from docx.shared import Mm
from docxtpl import DocxTemplate, InlineImage

import os


class DoccorpTemplate:

    def __init__(self, issue):
        self.doc = DocxTemplate(f"templates/{issue}.docx")
        self.issue = issue

    def my_render(self, render_dict: dict):
        # нужно пройтись по ключам и узнать, есть ли таблицы

        render_table = {}
        sign_list = []

        for render_key, render_val in render_dict.copy().items():
            if render_key.split('_')[0] == 'table':
                render_dict.pop(render_key)

                subx = self.doc.new_subdoc(f'templates/subs/{render_key}.docx')
                elements = list(subx.element.body)
                if len(elements) > 1 and not isinstance(elements[-2], CT_P):
                    subx.add_paragraph()

                render_dict[render_key] = subx
                render_table[render_key] = render_val

            if render_key.split('_')[0] == 'sign':
                render_dict.pop(render_key)
                decoded_bytes = base64.b64decode(render_val)
                with open(f'templates/{render_key}.png', 'wb') as fd:
                    fd.write(decoded_bytes)
                    fd.close()
                sign_list.append(render_key)
                render_dict[render_key] = ''

        self.doc.render(render_dict)

        for render_key in sign_list:
            self.doc.replace_pic(render_key, f'templates/{render_key}.png')
            os.remove(f'templates/{render_key}.png')

        self.doc.save(f'templates/{self.issue}_temp.docx')

        if render_table:
            self.doc = DocxTemplate(f"templates/{self.issue}_temp.docx")
            self.doc.render(render_table)
            self.doc.save(f'templates/{self.issue}_temp.docx')

        abv

        if os.name == 'nt':
            from docx2pdf import convert
            convert(f'templates/{self.issue}_temp.docx', f'templates/{self.issue}_temp.pdf')
        if os.name == 'posix':
            import subprocess
            command_uno = ['unoconvert', f'templates/{self.issue}_temp.docx', f'templates/{self.issue}_temp.pdf']
            command = ['libreoffice', '--headless', '--convert-to', 'pdf', '--outdir', 'templates/',
                       f'templates/{self.issue}_temp.docx']
            try:
                subprocess.check_output(command_uno)
            except Exception:
                subprocess.check_output(command)

        # получаем бинарник
        encoded = base64.b64encode(open(f'templates/{self.issue}_temp.pdf', 'rb').read())




        os.remove(f'templates/{self.issue}_temp.pdf')
        os.remove(f'templates/{self.issue}_temp.docx')

        return encoded
