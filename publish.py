# Publisher for markdown-based interactive media
import markdown
import zipfile
import os
import PyQt6
from PyQt6.QtWidgets import QApplication, QLabel, QPushButton, QProgressBar, QVBoxLayout, QWidget, QFileDialog, QCheckBox
import pathlib

def compress(directory_path: str, output_directory: str = None):
    if output_directory == None:
        output_directory =  pathlib.Path(os.path.dirname(os.path.normpath(directory_path))) / 'Published.zip'
    with zipfile.ZipFile(output_directory, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, directory_path))
        zipf.close()

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

def html_index(ordered_sources: list):
    ret = '''\t\t\t<p>This is the welcome page for viewing this publication. It contains a table of contents for quick navigation. At the end of each chapter are links to the previous and next chapters (where applicable). Chapters are presented in the order they should be read in.</p>
        </div>
        <div>
'''
    for source in ordered_sources:
        ret += f'\t\t\t<p><a href="./Chapters/{source}.html">{source}</a></p>\n'
    return ret

CSS = '''
p {
    text-indent: 48 !important;
    margin-top: 24 !important;
    margin-bottom: 24 !important;
}
div {
    margin-top: 36 !important;
    margin-bottom: 36 !important;
}
table#links {
    width: 100%;
}
td {
    border: 0px !important;
}
td.previous {
    width: 33% !important;
    text-align: start !important;
}
td.toc {
    width: 33% !important;
    text-align: center !important;
}
td.next {
    width: 33% !important;
    text-align: end !important;
}
'''

class Publisher():
    def __init__(self):
        # Establish instance variables
        self.source_directory = pathlib.Path('')
        self.output_directory = pathlib.Path('')

        # Set up app and window
        self.app = QApplication([])
        self.app.setStyle('Fusion')
        self.window = QWidget()
        self.window.setGeometry(100, 100, 600, 400)
        self.layout = QVBoxLayout()

        # Add UI Elements
        self.select_source_directory = QPushButton('Select Source Directory')
        self.select_source_directory.clicked.connect(self.on_select_source_directory_clicked)
        self.layout.addWidget(self.select_source_directory)

        self.select_output_directory = QPushButton('Select Output Directory')
        self.select_output_directory.clicked.connect(self.on_select_output_directory_clicked)
        self.layout.addWidget(self.select_output_directory)

        self.zip_selector = QCheckBox('Export .ZIP Archive as Well')
        self.layout.addWidget(self.zip_selector)

        self.displayed_source_directory = QLabel(f'Selected Source Directory: {self.source_directory}')
        self.layout.addWidget(self.displayed_source_directory)

        self.displayed_output_directory = QLabel(f'Selected Output Directory: {self.output_directory}')
        self.layout.addWidget(self.displayed_output_directory)

        self.publish = QPushButton('Publish')
        self.publish.clicked.connect(self.on_publish_clicked)
        self.layout.addWidget(self.publish)

        self.progress = QProgressBar()
        self.layout.addWidget(self.progress)


        # Display window
        self.window.setLayout(self.layout)
        self.window.show()
        self.app.exec()
    
    # Events
    def on_select_source_directory_clicked(self):
        self.source_directory = pathlib.Path(QFileDialog.getExistingDirectory(QWidget(), 'Select Source Directory'))
        self.displayed_source_directory.setText(f'Selected Source Directory: {self.source_directory}')
        self.progress.setValue(0)

    def on_select_output_directory_clicked(self):
        self.output_directory = pathlib.Path(QFileDialog.getExistingDirectory(QWidget(), 'Select Output Directory'))
        self.displayed_output_directory.setText(f'Selected Output Directory: {self.output_directory}')
        self.progress.setValue(0)

    def on_publish_clicked(self):
        order_path = self.source_directory / 'order.txt'

        # Get ordered sources
        ordered_sources = {}
        with open(order_path, 'r', encoding='utf8') as file:
            contents = file.readlines()
            ordered_sources = {x.strip(): self.source_directory / pathlib.Path(f'{x.strip()}.md') for x in contents}
            file.close()

        # Create index
        with open(self.output_directory / pathlib.Path('index.html'), 'w', encoding='utf8') as file:
            file.write(html_prologue('Welcome'))
            file.write(html_index(ordered_sources))
            file.write(html_epilogue())
            file.close()

        # Write stylesheet
        with open(self.output_directory / pathlib.Path('style.css'), 'w') as file:
            file.write(CSS)
            file.close()
        
        # Modify self.output_directory to store chapters in deeper directory
        chapters_path = self.output_directory / pathlib.Path('Chapters')

        if not chapters_path.exists():
            pathlib.Path.mkdir(chapters_path)
        
        # Act on each source file
        self.progress.setValue(0)
        self.progress.setMaximum(len(ordered_sources))

        v = 0
        for title, source in ordered_sources.items():
            v += 1
            self.progress.setValue(v)
            html = ''
            # Get source content
            with open(source, 'r', encoding='utf8') as file:
                html = str.join('\n', [f'\t\t\t{x}' for x in markdown.markdown(file.read().replace('---', 'SCENE_BREAK')).split('\n')])
                html = html.replace('\t<p>SCENE_BREAK</p>', '</div>\n\t\t<div>')
                file.close()
            # Add links
            titles = list(ordered_sources.keys())
            current_index = titles.index(title)
            previous = titles[current_index - 1] if current_index != 0 else ''
            next = titles[current_index + 1] if current_index != len(titles) - 1 else ''

            # Write html file
            with open(f'{chapters_path / pathlib.Path(title)}.html', 'w', encoding='utf8') as file:
                file.write(html_prologue(title))
                file.write(html)
                file.write(html_epilogue(previous, next))
                file.close()
        
        # Compress if requested
        if self.zip_selector.isChecked():
            compress(self.output_directory)

if __name__ == '__main__':
    publisher = Publisher()