# Publisher

## Basic Instructions
This tool publishes a set of markdown files to linked HTML webpages with minimalistic styling.

To use this tool, begin with a project structure like so:

Input files:
```
├── source/
│   ├── file1.md
│   ├── file2.md
│   ├── file3.md
│   ├── order.txt
```

The file `order.txt` must be present in the directory with the source Markdown files. This file tells the program in what order files should be read.

Output directories:
```
├── html/
│   ├── Chapters/
```

Here is an example which keeps the source and output together:
```
project/
├── source/
│   ├── file1.md
│   ├── file2.md
│   ├── file3.md
│   ├── order.txt
├── html/
│   ├── Chapters/
```

The resulting files will be structured as such:
```
project/
├── source/
│   ├── file1.md
│   ├── file2.md
│   ├── file3.md
│   ├── order.txt
├── html/
│   ├── index.html
│   ├── style.css
│   ├── Chapters/
│   │   ├── file1.html
│   │   ├── file2.html
│   │   ├── file3.html
```

## Installation
The program can be run with Python3 from the command line. However, this can lead to the cumbersome requirement of potentially long paths to source and output directories.

To run the program with Python, perform these steps:
1. Clone the repository
2. Within the cloned repository create a virtual environment. In this tutorial it is named `publisher_venv`
3. Activate the virtual environment with `./publisher_venv/Scripts/activate`
4. Install the dependencies with `python -m pip install -r requirements.txt`

## Building Release Binaries
### MacOS
1. Install [create-dmg](https://github.com/create-dmg/create-dmg) with `brew install create-dmg`
2. Navigate to the repository folder
3. Run `pyinstaller publish.py --onefile --windowed --icon=./assets/paper-plane.png`. Wait for this process to complete
4. Navigate to the `dist` folder
5. Run `create-dmg --volname "Publisher" --volicon "../assets/paper-plane.png" --app-drop-link 300 100 --icon "publish.app" 100 100 publish-macos-x.y.z.dmg publish.app`

### Windows
Windows binaries are not distributed at this time due to Windows Defender treating the program as malware. You can read more about it [here](https://www.reddit.com/r/learnpython/comments/e99bhe/comment/fahcknk/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button)