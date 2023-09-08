# yppm
Yingshaoxo Python Package Manager

## Install
```bash
sudo su
wget https://github.com/yingshaoxo/yppm/raw/main/Install.sh -O - | sudo bash
```

## Usage
### Create a project
```bash
yppm create_a_project
```

### Install a package
```bash
yppm install auto_everything
```

### Install all package
```bash
yppm install
```

### Run a script in package.json
```bash
yppm run ?
```

or 

```bash
yppm run <script_name>
```

### Build a project
```bash
yppm build
```

## Feature
* npm package.json like syntax.
* Can compile a python project into a single binary file.
* Has a backend and frontend template built_in (similar to SpringBoot).
* file_path based relative import supporting. (`import * as x from './lib.py'`)

## Based on
* venv: https://packaging.python.org/en/latest/key_projects/#standard-library-projects
* auto_everything