"""Local cancellable queue for the isolated NASEM engine."""
import json
from pathlib import Path
import subprocess
import tempfile
import threading
import time
import uuid

ROOT=Path(__file__).resolve().parents[2]
JOBS={}
PROCESSES={}
LOCK=threading.Lock()
SLOTS=threading.Semaphore(1)
JOB_TIMEOUT_SECONDS=600


def submit(scenario):
    if not isinstance(scenario,dict):raise ValueError('Cenário inválido.')
    with LOCK:
        if sum(j['estado'] in ('fila','executando') for j in JOBS.values())>=3:
            raise ValueError('Há três cenários na fila. Aguarde ou cancele um deles.')
        for key in list(JOBS):
            if JOBS[key]['estado'] not in ('fila','executando') and time.time()-JOBS[key]['criado']>3600:del JOBS[key]
        key=uuid.uuid4().hex
        JOBS[key]={'estado':'fila','progresso':'Aguardando o motor local.','criado':time.time(),'atualizado':time.time()}
    threading.Thread(target=run,args=(key,scenario),daemon=True).start()
    return key


def snapshot(key):
    with LOCK:
        if key not in JOBS:return None
        return dict(JOBS[key],segundos_decorridos=round(time.time()-JOBS[key]['criado'],1))


def cancel(key):
    with LOCK:
        if key not in JOBS:return None
        if JOBS[key]['estado'] not in ('fila','executando'):return dict(JOBS[key])
        JOBS[key].update(estado='cancelado',progresso='Cálculo cancelado.',atualizado=time.time(),resultado={'sucesso':False,'status':'cancelado','mensagem':'Cálculo cancelado pelo usuário.'})
        proc=PROCESSES.get(key)
    if proc is not None:
        try:proc.kill()
        except ProcessLookupError:pass
    return snapshot(key)


def run(key,scenario):
    with SLOTS:
        with LOCK:
            if JOBS[key]['estado']=='cancelado':return
            JOBS[key].update(estado='executando',progresso='Iniciando NASEM…',atualizado=time.time())
        runtime=ROOT/'helpful_scripts/interface_rufas/.venv_nasem/bin/python'
        worker=ROOT/'helpful_scripts/interface_rufas/worker_nasem.py'
        proc=None;timer=None;timed_out=threading.Event()
        try:
            with tempfile.TemporaryFile(mode='w+t') as errors:
                proc=subprocess.Popen([str(runtime),'-u',str(worker)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=errors,text=True,cwd=ROOT)
                with LOCK:
                    PROCESSES[key]=proc
                    cancelled=JOBS[key]['estado']=='cancelado'
                if cancelled:proc.kill();return
                def stop_timeout():
                    timed_out.set()
                    try:proc.kill()
                    except ProcessLookupError:pass
                timer=threading.Timer(JOB_TIMEOUT_SECONDS,stop_timeout);timer.daemon=True;timer.start()
                proc.stdin.write(json.dumps(scenario));proc.stdin.close()
                result=None
                for line in proc.stdout:
                    event=json.loads(line)
                    if 'progresso' in event:
                        with LOCK:
                            if JOBS[key]['estado']!='cancelado':JOBS[key].update(progresso=event['progresso'],atualizado=time.time())
                    if 'resultado' in event:result=event['resultado']
                proc.wait()
                with LOCK:
                    if JOBS[key]['estado']=='cancelado':return
                if result is None:
                    errors.seek(0);detail=errors.read()[-1500:]
                    result={'sucesso':False,'status':'limite_tempo' if timed_out.is_set() else 'falha_motor','mensagem':'Tempo máximo de 10 minutos atingido. Reduza o horizonte/intervalos.' if timed_out.is_set() else 'O motor foi interrompido. Confira o diagnóstico técnico.','detalhe_tecnico':detail}
            # Preserve failed diagnostics as well as validated plans, locally.
            folder=ROOT/'output/estudo_dieta';folder.mkdir(parents=True,exist_ok=True)
            target=folder/f'nasem_{key}.json'
            target.write_text(json.dumps({'cenario':scenario,**result},ensure_ascii=False,indent=2,allow_nan=False))
            result['arquivo']=str(target)
            with LOCK:
                if JOBS[key]['estado']!='cancelado':JOBS[key].update(estado='concluido' if result.get('sucesso') else 'falhou',resultado=result,progresso='Cálculo finalizado.',atualizado=time.time())
        except Exception as exc:
            with LOCK:
                if JOBS[key]['estado']!='cancelado':JOBS[key].update(estado='falhou',resultado={'sucesso':False,'status':'erro','mensagem':str(exc)},progresso='Cálculo interrompido.',atualizado=time.time())
        finally:
            if timer is not None:timer.cancel()
            if proc is not None and proc.poll() is None:proc.kill();proc.wait()
            with LOCK:PROCESSES.pop(key,None)
