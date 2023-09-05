# CndScaffold

# Why use CndScaffold

CndScaffold is a python lib, designed to help management of GitOps process.
With CndScaffold, you need data and template definition and then CndScaffold do the magic and generate content

# New in 2.0.0
CndScaffold are now compatible with jinja2 engine (https://realpython.com/primer-on-jinja-templating/)

It allow use more complexe structure in file

# Requirements

This lib use 
- CndIo : This lib allow you to easilly push conten on gitlab/azuredevops or localfile
- CndPrint : This lib to manage display of alert message

# How to use it
```
source = {
	'project_id': 'gitlab-source-project-id',
	'definition': 'org-demo1_product1',
	'branch': 'main',
}
target = {
	'project_id': 'gitlab-target-project-id',
	'folder': 'home',
	'branch': 'main',
}

data_to_replace = {
	'env': ['alpha', 'gamma'],
	'client': [{'name': 'A', 'token': 'B'}, {'name': 'A', 'token': 'B'}],
	'app': 'beta',
	'abc': 'def',
	'yaml': {
		'abc': 'def',
		'ghi': ['jkl', 'lmo']
	}
}

level = "Trace"
_print = cndprint.CndPrint(level=level, silent_mode=True)
provider = cnd_io.CndProviderLocalfile(creds={}, print=_print)
cnd_io = cnd_io.CndIO(provider, print=_print)

self.cnd_scaffold = cnd_scaffold.CndScaffold(source, target, data_to_replace, cnd_io, print=_print)
self.cnd_scaffold.build()
```

# Usage with array of item with jinja2

in model file
```
module "acl-org-{{ app }}-{{ org_read.org_shortname }}" {
  source  = "./modules/acl-org"
  org = "{{ org_read.org }}"
  action = "read"
}
```

Example of data to works with model file
```
data_to_replace = {
	'app': 'beta',
	'org_read': [
		{
			'org': 'def',
			'org_shortname': 'd'
		},
		{
			'org': 'abc',
			'org_shortname': 'a'
		}
	]
}
```
