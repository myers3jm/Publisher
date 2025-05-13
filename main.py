import os
import zipfile
import markdown
import io
import pathlib
from flask import Flask, render_template, flash, request, redirect, url_for

app = Flask(__name__)

def html_prologue(title: str):
    return f'''
<html>
    <head>
        <link rel="stylesheet" href="../style.css">
        <link rel="stylesheet" href="https://unpkg.com/simpledotcss/simple.min.css">
        <title>{title}</title>
    </head>
    <body>
        <div>
'''

def html_epilogue(previous: str = None, next: str = None):
    previous_link = f'<a href="{previous}.html">{previous}</a>' if previous != '' else ''
    next_link = f'<a href="{next}.html">{next}</a>' if next != '' else ''
    ret = '\t\t</div>'
    if previous != None or next != None:
        ret += f'''\t\t<div>
            <table id="links">
                <tr>
                    <td class="previous">
                        {previous_link}
                    </td>
                    <td class="toc"><a href="../index.html">Table of Contents</a></td>
                    <td class="next">
                        {next_link}
                    </td>
                </tr>
            </table>
        </div>
    </body>
</html>
'''
    return ret

def create_html(file):
    html = '\t\t<div>\n'
    html += str.join('\n', [f'\t\t\t{x}' for x in markdown.markdown(file.read().replace('---', 'SCENE_BREAK')).split('\n')])
    html = html.replace('\t<p>SCENE_BREAK</p>', '</div>\n\t\t<div>')
    html += '\t\t</div>'
    print(render_template('published.html', content=html))

@app.route('/')
def index():
    return render_template('index.html',mytext='Hello')

@app.post('/publish')
def publish():
    files = request.files.getlist("upload")
    
    # Error - no files uploaded
    if not files:
        return {'error': 'no files'}, 400
    
    # Error - too few files
    if len(files) < 2:
        return {'error': 'too few files'}, 400
    
    # Error - no order.txt present
    if 'order.txt' not in [x.filename for x in files]:
        return {'error': 'no order.txt'}, 400
    
    bundle = io.BytesIO()
    with zipfile.ZipFile(bundle, mode='w', compression=zipfile.ZIP_DEFLATED) as z:
        md_sources = [x for x in files if '.md' in x.filename]
        order = [x for x in files if 'order.txt' == x.filename][0]

        # Order sources according to order.txt
        ordered_sources = {}
        with open(order, 'r', encoding='utf8') as order_file:
            contents = order_file.readlines()
            ordered_sources = {x.strip(): pathlib.Path(x).stem for x in contents}



        for file in md_sources:
            stem = pathlib.Path(file.filename).stem
            z.writestr(f'{stem}.html', create_html(file))

if __name__ == '__main__':
    app.run()