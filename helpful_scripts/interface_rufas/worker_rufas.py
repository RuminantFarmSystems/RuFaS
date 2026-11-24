"""Headless native RuFaS worker; stdout contains JSON-lines only."""
import os
import sys
import json
import tempfile
from contextlib import redirect_stdout

# The RuFaS graph module selects Tk whenever DISPLAY exists. This worker never
# opens graphics, so select its documented headless path in this process only.
os.environ.pop('DISPLAY',None)
os.environ.setdefault('MPLCONFIGDIR',str(__import__('pathlib').Path(tempfile.gettempdir())/'rufas-matplotlib'))
from rufas_solver import planejar

def emit(payload):
    print(json.dumps(payload,ensure_ascii=False,allow_nan=False),flush=True,file=sys.__stdout__)

if __name__=='__main__':
    try:
        scenario=json.load(sys.stdin)
        with redirect_stdout(sys.stderr):
            result=planejar(scenario,progress=lambda message:emit({'progresso':message}))
        emit({'resultado':result})
    except Exception as exc:
        import traceback
        traceback.print_exc(file=sys.stderr)
        emit({'resultado':{'sucesso':False,'status':'erro_motor','mensagem':str(exc)}})
        sys.exit(1)
