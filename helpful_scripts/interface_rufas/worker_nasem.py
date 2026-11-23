"""Isolated JSON-lines worker. Invoke with the dedicated NASEM Python environment."""
import json
import sys
from nasem_solver import planejar


def emit(payload):
    print(json.dumps(payload,ensure_ascii=False,allow_nan=False),flush=True)


if __name__=='__main__':
    try:
        scenario=json.load(sys.stdin)
        result=planejar(scenario,progress=lambda message:emit({'progresso':message}))
        emit({'resultado':result})
    except Exception as exc:
        emit({'resultado':{'sucesso':False,'mensagem':str(exc)}})
        sys.exit(1)
