import io
import json
import threading
import time
import unittest
from unittest.mock import patch,MagicMock
import jobs_nasem as jobs
from nasem_solver import Formulator, SearchTimeout

class ReliabilityTests(unittest.TestCase):
    def test_stock_is_total_for_the_horizon(self):
        f=Formulator({'estoques':{'51':10000}})
        j=f.f.index[f.f.id==51][0]
        self.assertAlmostEqual(f.bounds[j][1],10000/(100*30))
        seed,fail=f._linear_seed([0])
        self.assertIsNone(fail)
        self.assertLessEqual(seed[j],f.bounds[j][1]+1e-8)

    def test_impossible_budget_fails_before_nutrition_calls(self):
        f=Formulator({'orcamento_dia':1})
        result,_=f.solve(0)
        self.assertFalse(result['sucesso']);self.assertEqual(result['status'],'inviavel_linear')
        self.assertEqual(f.calls,0)

    def test_zero_all_stocks_cannot_be_a_valid_diet(self):
        f=Formulator({})
        stocks={str(int(i)):0 for i in f.f.id}
        f=Formulator({'estoques':stocks})
        result,_=f.solve(0)
        self.assertFalse(result['sucesso']);self.assertEqual(f.calls,0)

    def test_clock_is_checked_during_nutritional_evaluations(self):
        f=Formulator({});f.deadline=time.monotonic()-1
        with self.assertRaises(SearchTimeout):f.evaluate([1]*len(f.f),0)

    def test_queue_cancel_does_not_start_a_process(self):
        with patch.object(jobs.threading,'Thread'):
            key=jobs.submit({})
        self.assertEqual(jobs.cancel(key)['estado'],'cancelado')
        with patch.object(jobs.subprocess,'Popen') as popen:jobs.run(key,{})
        popen.assert_not_called()

    def test_running_cancel_kills_the_worker(self):
        with patch.object(jobs.threading,'Thread'):key=jobs.submit({})
        proc=MagicMock()
        with jobs.LOCK:
            jobs.JOBS[key]['estado']='executando';jobs.PROCESSES[key]=proc
        self.assertEqual(jobs.cancel(key)['estado'],'cancelado');proc.kill.assert_called_once()
        with jobs.LOCK:jobs.PROCESSES.pop(key,None)

    def test_worker_timeout_is_terminal(self):
        with patch.object(jobs.threading,'Thread'):key=jobs.submit({})
        killed=threading.Event()
        class Process:
            stdin=io.StringIO()
            def __init__(self):self.stdout=self.lines()
            def lines(self):
                killed.wait(1)
                return
                yield ''
            def kill(self):killed.set()
            def wait(self):return -9
            def poll(self):return -9 if killed.is_set() else None
        with patch.object(jobs,'JOB_TIMEOUT_SECONDS',.02),patch.object(jobs.subprocess,'Popen',return_value=Process()),patch.object(jobs.ROOT.__class__,'mkdir'),patch.object(jobs.ROOT.__class__,'write_text'):
            jobs.run(key,{})
        result=jobs.snapshot(key)
        self.assertEqual(result['estado'],'falhou');self.assertEqual(result['resultado']['status'],'limite_tempo')
        self.assertNotIn(key,jobs.PROCESSES)

if __name__=='__main__':unittest.main()
