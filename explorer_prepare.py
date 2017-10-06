import jsl
import json
import yaml

import os
import sys


def compile_json_schemas(path):
    os.chdir(path)
    sys.path.append(os.path.abspath('.'))
    r = {}
    for f in os.listdir('.'):
        if f.endswith('.py'):
            with open(f, 'r') as of:
                local = {}
                exec(compile(of.read(), f, 'exec'), local)
                for k, v in local.items():
                    base = getattr(v, '__base__', None)
                    
                    want = not k.startswith('_') and isinstance(v, jsl.document.DocumentMeta)
                    want |= getattr(getattr(base, '__base__', None), '__name__', None) == 'BaseSchemaField'
                    want &= k != 'Document'

                    if want:
                        yield k, v(), f


actors = []
schemas = []
for name in os.listdir('src/actors/'):
    fp = os.path.join('src/actors/', name, '_actor.yaml')
    with open(fp, 'r') as of:
        actors.append(
            yaml.load(of)
        )
        actors[-1]['name'] = name
for name, obj, file_ in compile_json_schemas('src/schema/'):
    schemas.append(
        {'name': name, 'schema': obj.get_schema()}
    )

out = {
    'schemas': schemas,
    'actors': actors
}

json.dump(out, sys.stdout, indent=3)
