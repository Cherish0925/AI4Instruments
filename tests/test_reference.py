import asyncio
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ai4instruments import Node, Operation, Runtime, Trace, run_dag
from ai4instruments.optics import OpticalBench, align, quantity


class ReferenceTests(unittest.IsolatedAsyncioTestCase):
    async def test_command_is_not_an_observation(self):
        bench = OpticalBench()
        result = await bench.runtime.invoke("x.write_target", {"target": quantity(1, "mm")})
        self.assertEqual(result["commanded"]["target"]["value"], 1)
        self.assertNotIn("observed", result)
        self.assertEqual(bench.axes["x"].position, 0)
        sample = await bench.runtime.invoke("x.read_position")
        self.assertEqual(sample["observed"]["position"]["value"], 0.75)

    async def test_invalid_units_ranges_and_nonfinite_values_do_not_mutate_state(self):
        bench = OpticalBench()
        for argument in (quantity(1, "V"), quantity(3, "mm"), quantity(float("nan"), "mm"),
                         quantity(True, "mm"), {"value": 1, "unit": "mm", "extra": 0}):
            with self.assertRaises(ValueError):
                await bench.runtime.invoke("x.write_target", {"target": argument})
        self.assertEqual(bench.axes["x"].target, 0)
        self.assertEqual(len(bench.trace.events), 1)

    async def test_independent_nodes_overlap_and_dependency_waits(self):
        runtime = Runtime(Trace({"run_id": "concurrency-test"}))
        entered, completed = set(), set()
        both_entered = asyncio.Event()

        async def independent(values, call_id):
            entered.add(call_id)
            if len(entered) == 2:
                both_entered.set()
            await both_entered.wait()
            completed.add(call_id)
            return {"done": True}

        async def dependent(values, call_id):
            self.assertEqual(len(completed), 2)
            return {"done": True}

        runtime.register(Operation("independent", "Basic Operations", "", {}, independent))
        runtime.register(Operation("dependent", "Standard Operations", "", {}, dependent))
        result = await asyncio.wait_for(run_dag(runtime, [
            Node("c", "dependent", after=("a", "b")),
            Node("a", "independent"), Node("b", "independent")]), timeout=1)
        self.assertTrue(result["c"]["done"])

    async def test_invalid_dependency_graph_starts_nothing(self):
        bench = OpticalBench()
        for nodes in ([Node("a", "x.read_position", after=("b",)),
                       Node("b", "y.read_position", after=("a",))],
                      [Node("a", "x.read_position", after=("missing",))],
                      [Node("a", "x.read_position"), Node("a", "y.read_position")]):
            with self.assertRaises(ValueError):
                await run_dag(bench.runtime, nodes)
        self.assertEqual(len(bench.trace.events), 1)

    async def test_failed_node_cancels_and_drains_independent_work(self):
        runtime = Runtime(Trace({"run_id": "failure-test"}))
        active = asyncio.Event()
        cleaned = asyncio.Event()

        async def waiting(values, call_id):
            active.set()
            try:
                await asyncio.Event().wait()
            finally:
                cleaned.set()

        async def failing(values, call_id):
            await active.wait()
            raise RuntimeError("test fault")

        runtime.register(Operation("wait", "Basic Operations", "", {}, waiting))
        runtime.register(Operation("fail", "Basic Operations", "", {}, failing))
        with self.assertRaisesRegex(RuntimeError, "test fault"):
            await run_dag(runtime, [Node("a", "wait"), Node("b", "fail")])
        self.assertTrue(cleaned.is_set())
        self.assertEqual(len([e for e in runtime.trace.events if e["event"] == "failed"]), 2)

    async def test_deterministic_trace_and_closed_loop_evidence(self):
        bench, summary = await align(17)
        repeat, repeated_summary = await align(17)
        self.assertEqual(summary, repeated_summary)
        self.assertEqual(bench.trace.events, repeat.trace.events)
        self.assertGreater(summary["final_power_uW"], summary["initial_power_uW"] * 3)
        started = {e["call_id"]: e for e in bench.trace.events if e["event"] == "started"}
        finished = {e["call_id"]: e for e in bench.trace.events if e["event"] == "completed"}
        self.assertEqual(set(started), set(finished))
        measurements = {}
        for event in finished.values():
            if event["operation_id"] == "detector.acquire":
                result = event["result"]
                measurements[result["measurement_id"]] = result["observed"]["power"]["value"]
        evaluations = [e for e in bench.trace.events if e["event"] == "evaluation"]
        self.assertEqual(len(evaluations), summary["evaluations"])
        for event in evaluations:
            self.assertEqual(event["score"], measurements[event["measurement_id"]])
        for call in started.values():
            if call["parent_id"] is not None:
                self.assertIn(call["parent_id"], started)
                self.assertLess(call["sequence"], finished[call["parent_id"]]["sequence"])

    async def test_published_capabilities_match_implementation(self):
        path = Path(__file__).resolve().parents[1] / "examples" / "capabilities.json"
        self.assertEqual(json.loads(path.read_text()), OpticalBench().capabilities())


if __name__ == "__main__":
    unittest.main()
