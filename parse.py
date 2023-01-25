import os
from cerberus import Validator
from yaml import load
from markdown2 import markdown

# Location for service files to be loaded from
LOAD_DIR = '/etc/ents/services'

# Locations to which SVG files should be resolved
SVG_DIR = '/etc/ents/landing-parser/svg'

# PyYaml comes in multiple versions so we need to rename a couple of things depending on how its run
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

PAGE_CSS = """
* {
    font-family: 'Raleway', sans-serif;
    box-sizing: border-box;
}

code{
    font-family: monospace;
    background: #ededed;
    padding: 2px 5px;
    border-radius: 3px;
}

body,
html {
    margin: 0;
    padding: 0;
}

h1 {
    width: 100%;
    background: #eaeaea;
    padding: 30px;
    margin: 0;
}

.content {
    width: 70%;
    margin: 0 auto;
}

h2 {
    border-top: 1px solid black;
    padding-top: 10px;
}

.boxes {
    display: flex;
    flex-direction: row;
    flex-wrap: wrap;
}

.boxes>a {
    display: inline-flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    width: 10pc;
    height: 10pc;
    /* background: red; */
    border-radius: 10px;
    border: 1px solid gainsboro;
}

.boxes>a,
.boxes>a * {
    color: black;
    text-decoration: none;
}

.boxes>a svg {
    width: 3pc;
}

.boxes>a h3 {
    margin: 0;
    padding: 0;
    padding-top: 10px;
}

.boxes>a span {
    text-align: center;
    font-size: 0.6em;
    padding: 10px;
    padding-bottom: 0;
}

.services .service {
    display: flex;
    flex-direction: row;
    align-items: center;
    padding: 20px;
    border-radius: 10px;
    border: 1px solid gainsboro;
    margin-bottom: 20px;
}

.services .service .icon {
    flex-basis: 60px;
    flex-grow: 0;
    flex-shrink: 0;
}

.services .service .icon svg {
    width: 45px;
}

.services .service h3 {
    margin: 0;
    padding: 0;
}

.services .service .usage {
    margin-left: 20px;
}

@media screen and (max-width: 820px) {
    .content{
        width: unset;
        padding: 0 20px;
    }
}"""
PAGE_TEMPLATE = """
<!DOCTYPE html>
<html>

<head>
    <meta charset='utf-8'>
    <meta http-equiv='X-UA-Compatible' content='IE=edge'>
    <title>Page Title</title>
    <meta name='viewport' content='width=device-width, initial-scale=1'>

    <style>
        {css}
    </style>
</head>

<body>

    <h1>Ents Crew Utility Pi</h1>

    <div class="content">
        <h2>Launcher</h2>
        <div class="boxes">
            {boxes}
        </div>

        <h2>Services</h2>
        <div class="services">
            {services}
        </div>
    </div>

</body>

</html>"""

WEB_SERVICE_TEMPLATE = """
<a href="{link}">
    {icon}
    <h3>{name}</h3>
    <span>{description}</span>
</a>"""

SERVICE_TEMPLATE = """
<div class="service">
    <div class="icon"> {icon} </div>
    <div class="description">
        <h3>{name}</h3>
        {description}
        <div class="usage">
            <h4>Usage</h4>
            {usage}
        </div>
        <a href="{link}">View on GitHub</a>
    </div>
</div>"""

# Cerberus schemas for service files
WEB_SERVICE_SCHEMA = {
    'mode': {'type': 'string', 'allowed': ['web'], 'required': True},
    'name': {'type': 'string', 'required': True},
    'link': {'type': 'string', 'required': True},
    'description': {'type': 'string', 'required': True},
    'icon': {'type': 'string', 'default': 'help-circle-outline'}
}

SERVICE_SCHEMA = {
    'mode': {'type': 'string', 'allowed': ['service'], 'required': True},
    'name': {'type': 'string', 'required': True},
    'description': {'type': 'string', 'required': True},
    'usage': {'type': 'string', 'required': True},
    'github': {'type': 'string', 'required': True, 'regex': '^([a-zA-Z\d]{1}[-a-zA-Z\d]+)(/){1}([\-\w]+)$'},
    'icon': {'type': 'string', 'default': 'help-circle-outline'}
}

WEB_SERVICE_VALIDATOR = Validator(WEB_SERVICE_SCHEMA)
SERVICE_VALIDATOR = Validator(SERVICE_SCHEMA)

# Collected valid services ready for rendering
web_services = []
services = []

# Take every file in the service folder
for file in os.listdir(LOAD_DIR):
    file_path = os.path.join(LOAD_DIR, file)
    with open(file_path, 'r') as f:
        try:
            # Try parse as yaml
            data = load(f, Loader=Loader)

            if 'mode' not in data or data['mode'] not in ['web', 'service']:
                print(
                    'Error in file {} - does not contain mode, or mode is an invalid value'.format(file_path))
                continue

            # Validate appropriately
            if data['mode'] == 'web':
                if WEB_SERVICE_VALIDATOR.validate(data):
                    web_services.append(data)
                else:
                    print("Error in file {} - does not match schema".format(file_path))
            else:
                if SERVICE_VALIDATOR.validate(data):
                    services.append(data)
                else:
                    print("Error in file {} - does not match schema".format(file_path))
            
        except Exception as e:
            print(f"Failed to parse file: {f}")
            print(e)

# Load the fallback SVG
svg_options = os.listdir(SVG_DIR)
with open(os.path.join(SVG_DIR, 'help-circle-outline.svg'), 'r') as f:
    help_circle_outline = f.read().replace('width="24" height="24"', '')

# Replace every icon with the SVG contents if found or the fallback if its now
for entry in services + web_services:
    if 'icon' in entry:
        if entry['icon'] + '.svg' not in svg_options:
            print('Icon {} is not valid - removing'.format(entry['icon']))
            entry['icon'] = help_circle_outline
        else:
            with open(os.path.join(SVG_DIR, entry['icon'] + '.svg'), 'r') as f:
                entry['icon'] = f.read().replace('width="24" height="24"', '')
    else:
        entry['icon'] = help_circle_outline


def format_web(entry):
    return WEB_SERVICE_TEMPLATE.format(**entry)

def format_service(entry):
    return SERVICE_TEMPLATE.format(**{
        'name': entry['name'],
        'description': markdown(entry['description']),
        'usage': markdown(entry['usage']),
        'link': 'https://github.com/' + entry['github'],
        'icon': entry['icon']
    })

# Render to HTML
web_html = list(map(format_web, web_services))
service_html = list(map(format_service, services))

# And piece together the final HTML file
with open("/var/www/html/index.html", "w") as f:
    f.write(PAGE_TEMPLATE.format(boxes=''.join(web_html), services=''.join(service_html), css=PAGE_CSS))
