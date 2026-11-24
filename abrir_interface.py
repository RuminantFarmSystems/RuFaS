#!/usr/bin/env python3
"""Aplicação de pesquisa local. Execute: python abrir_interface.py [--port 8080]."""
import argparse
import csv
import hashlib
import io
import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from helpful_scripts.interface_rufas.solver_dinamico import (
    carregar_dataframe_alimentos, otimizar_dieta, gerar_curva_otimizacao_leite,
)

from helpful_scripts.interface_rufas.jobs_nasem import submit, snapshot, cancel

ROOT = Path(__file__).resolve().parent
ALLOWED = {"peso_vivo", "leite_kg", "gordura_pct", "proteina_pct", "del_dias",
           "precos_custom", "alimentos_bloqueados", "teto_caroco", "preco_leite_kg"}


def calcular(body):
    if not isinstance(body, dict) or set(body) - (ALLOWED | {"curva"}):
        raise ValueError("Parâmetros desconhecidos.")
    args = {k: v for k, v in body.items() if k in ALLOWED}
    args["precos_custom"] = {int(k): float(v) for k,v in args.get("precos_custom", {}).items()}
    result = otimizar_dieta(**args)
    if body.get("curva"):
        result["curva"] = gerar_curva_otimizacao_leite(**args)
    files = ["input/data/feed/NRC_comp.csv", "helpful_scripts/nrc2001_dieta_lp/alimentos_precos.csv"]
    result["proveniencia"] = {f: hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in files}
    result["cenario"] = args
    return result


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT/"interface"), **kwargs)

    def send_json(self, code, data):
        payload = json.dumps(data, ensure_ascii=False, allow_nan=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        if self.path == '/api/nasem/alimentos':
            self.send_json(200,json.loads((ROOT/'helpful_scripts/interface_rufas/alimentos_nasem.json').read_text()))
            return
        if self.path.startswith('/api/nasem/jobs/'):
            job = snapshot(self.path.rsplit('/',1)[-1])
            self.send_json(200 if job else 404, job or {'mensagem':'Cálculo não encontrado.'})
            return
        if self.path == "/api/alimentos":
            f,q,p = carregar_dataframe_alimentos()
            self.send_json(200, {"alimentos": f.to_dict("records"), "premix": {"kg_ms": q, "preco": p}})
        elif self.path == "/api/status":
            self.send_json(200, {"status": "online", "modo": "local", "NASEM": "motor independente nasem_dairy 1.0.2"})
        else:
            super().do_GET()

    def do_POST(self):
        # Reject cross-origin browser writes; server binds only to loopback.
        origin = self.headers.get("Origin")
        if origin and origin != "http://" + self.headers.get("Host", ""):
            self.send_json(403, {"sucesso": False, "mensagem": "Origem não autorizada."})
            return
        try:
            size = int(self.headers.get("Content-Length", 0))
            if not 0 < size <= 100000:
                raise ValueError("Tamanho de solicitação inválido.")
            body = json.loads(self.rfile.read(size))
            if self.path.startswith('/api/nasem/jobs/') and self.path.endswith('/cancel'):
                job=cancel(self.path.split('/')[-2])
                self.send_json(200 if job else 404,job or {'mensagem':'Cálculo não encontrado.'})
                return
            if self.path == '/api/nasem/jobs':
                key=submit(body)
                self.send_json(202, {'job_id':key})
                return
            if self.path not in ("/api/otimizar", "/api/exportar"):
                self.send_json(404, {"sucesso": False, "mensagem": "Rota inexistente."})
                return
            result = calcular(body)
            if self.path == "/api/exportar" and result["sucesso"]:
                # Export only the validated independent scenario, never overwrite RuFaS inputs.
                folder = ROOT/"output"/"estudo_dieta"
                folder.mkdir(parents=True, exist_ok=True)
                key = hashlib.sha256(json.dumps(result["cenario"], sort_keys=True).encode()).hexdigest()[:12]
                target = folder/f"cenario_{key}.json"
                target.write_text(json.dumps(result, ensure_ascii=False, indent=2))
                result["arquivo"] = str(target)
            self.send_json(200, result)
        except (ValueError, TypeError, KeyError, OverflowError) as exc:
            self.send_json(400, {"sucesso": False, "mensagem": str(exc)})
        except Exception:
            self.send_json(500, {"sucesso": False, "mensagem": "Falha interna. Consulte o terminal."})
            import traceback
            traceback.print_exc()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"Estudo de dietas: http://127.0.0.1:{args.port} — Ctrl+C para encerrar", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        # Stop this application's workers when the local server is closed.
        from helpful_scripts.interface_rufas.jobs_nasem import JOBS, LOCK
        with LOCK: active=[key for key,job in JOBS.items() if job['estado'] in ('fila','executando')]
        for key in active: cancel(key)
        server.server_close()


if __name__ == "__main__":
    main()
