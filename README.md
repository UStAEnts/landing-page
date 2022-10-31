# landing-page

* [Dependencies](#dependencies)
* [`incron` Configuration](#incron-configuration)
* [Configuration Files](#configuration-files)
    * [Services](#services)
    * [Web Applications](#web-applications)
    * [Icons](#icons)
* [Examples](#examples)
    * [Service](#service)
    * [Web](#web)

This project automatically generates a landing page for the EntsPi based on the services defined in `/etc/ents/services`. This is designed to be integrated with `incron` via `incrontab` which can be used to trigger the generation script on file change. 

## Dependencies

This project depends on the following packages

* Cerberus
* markdown2
* PyYAML

Which should be installable via

```bash
$ python3 -m pip install cerberus markdown2 pyyaml
```

## `incron` Configuration

Using `incrontab -e` add the following line

```
/etc/ents/services	IN_MODIFY,IN_MOVED_TO	/usr/bin/python3 /etc/ents/landing-parser/parse.py > /var/log/ents/landing-page.log 2>&1
```

This will cause the parse script to be called every time a file is moved into the services folder or is edited. This may not catch all cases but seemed to cover the uses we had in mind. 

## Configuration Files

Services files are stored in `/etc/ents/services` and all end in `.service.yml` as convention. However technically _any_ file in this folder will be opened and read as a YAML file. Files are broken into two categories: services and web applications. 

### Services

Services are things running on the Pi which are _not_ accessible via a web interface. These sections are designed to be freeform and explain the purpose of the service as well as linking to the code on GitHub. These files take the format (in TypeScript notation)

```
mode: 'service',
name: string,
description: string,
usage: string,
github: string, // regex: '^([a-zA-Z\d]{1}[-a-zA-Z\d]+)(/){1}([\-\w]+)$' - should be in the form user/repository
icon?: string,
```

The description and usage entries of these files are parsed as markdown allowing for code blocks and HTML blocks. 

### Web Applications

Web applications should be accessible on the pi. These are rendered as small cards that link to the service, therefore the name and description should be short - generally a single line description. The idea is that the service should be usable as soon as you navigate to it. 

```
mode: 'web',
name: string,
link: string,
description: string,
icon?: string
```

Links should be fully qualified. 

### Icons

Icons are based on the Material Design Icons library and should be the simple name of any icon available at https://materialdesignicons.com/ (ie `mirror-variant`). 

## Examples

### Service

```yaml
mode: service
name: Terminal Server
description: UDP terminal server which substitutes parameters from a UDP packet into a command specified in the config file. Current commands include `projector-control` which takes the three parameters as described in the projector control service
usage: UDP Port 8889 - Packets are in the format `command:params`. Parameters are defined by the schema regex. To issue a command with no parameters you send `command:`. The colon is always required. For example to execute the two commands shown you would issue packets with `demo:` and `demo:a`
github: ents-crew/terminal-server
icon: server
```

### Web

```yaml
mode: web
name: X32 Reflector
description: Redirect X32 parameter OSC packets to your device
link: http://10.1.10.11/x32
icon: mirror-variant
```