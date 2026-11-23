"""Local background process queue, isolated from RuFaS Python dependencies."""
import json
from pathlib import Path
import subprocess
import threading
import time
import uuid

ROOT=Path(__file__).resolve().parents[2]
JOBS={}
LOCK=threading.Lock()
SLOTS=threading.Semaphore(1)


def submit(scenario):
    if not isinstance(scenario,dict):
        raise ValueError('Cenário inválido.')
    with LOCK:
        if sum(j['estado'] in ('fila','executando') for j in JOBS.values())>=3:
            raise ValueError('Há três cenários na fila. Aguarde a conclusão.')
        for key in list(JOBS):
            if JOBS[key]['estado'] not in ('fila','executando') and time.time()-JOBS[key]['criado']>3600:
                del JOBS[key]
        key=uuid.uuid4().hex
        JOBS[key]={'estado':'fila','progresso':'Aguardando o motor local.','criado':time.time()}
    threading.Thread(target=run,args=(key,scenario),daemon=True).start()
    return key


def snapshot(key):
    with LOCK:
        return dict(JOBS[key]) if key in JOBS else None


def run(key,scenario):
    with SLOTS:
        with LOCK:JOBS[key].update(estado='executando',progresso='Iniciando NASEM…')
        runtime=ROOT/'helpful_scripts/interface_rufas/.venv_nasem/bin/python'
        worker=ROOT/'helpful_scripts/interface_rufas/worker_nasem.py'
        proc=None
        try:
            proc=subprocess.Popen([str(runtime),'-u',str(worker)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,text=True,cwd=ROOT)
            timer=threading.Timer(1800,proc.kill);timer.start()
            proc.stdin.write(json.dumps(scenario));proc.stdin.close()
            result=None
            for line in proc.stdout:
                event=json.loads(line)
                if 'progresso' in event:
                    with LOCK:JOBS[key]['progresso']=event['progresso']
                if 'resultado' in event:result=event['resultado']
            proc.wait();timer.cancel()
            if result is None:
                raise RuntimeError('Motor interrompido ou limite de 30 minutos atingido. Reduza o horizonte.')
            if result.get('sucesso'):
                folder=ROOT/'output/estudo_dieta';folder.mkdir(parents=True,exist_ok=True)
                target=folder/f'nasem_{key}.json'
                target.write_text(json.dumps(result,ensure_ascii=False,indent=2))
                result['arquivo']=str(target)
            with LOCK:JOBS[key].update(estado='concluido' if result.get('sucesso') else 'falhou',resultado=result,progresso='Cálculo finalizado.')
        except Exception as exc:
            if proc is not None and proc.poll() is None:proc.kill()
            with LOCK:JOBS[key].update(estado='falhou',resultado={'sucesso':False,'mensagem':str(exc)},progresso='Cálculo interrompido.')
