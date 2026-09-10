"""Offline adapter tests. No provider, network, or real child processes."""
import argparse
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("dispatch", ROOT / "skills/agent-brain/scripts/dispatch.py")
dispatch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dispatch)


class DispatchTests(unittest.TestCase):
    def test_no_tools_and_no_automatic_subagents(self):
        for adapter in ("claude-code", "grok"):
            cmd = dispatch.command(adapter, "agent.exe", "model; literal", "low")
            self.assertEqual(cmd[cmd.index("--model") + 1], "model; literal")
            self.assertEqual(cmd[cmd.index("--tools") + 1], "")
            self.assertEqual(cmd[cmd.index("--max-turns") + 1], "1")
        self.assertIn("--no-subagents", dispatch.command("grok", "grok.exe", "grok", "low"))

    def test_per_model_usage_includes_auxiliary_without_aggregate(self):
        body = {"result": "OK", "usage": {"input_tokens": 999}, "total_cost_usd": 99,
                "modelUsage": {"sonnet": {"inputTokens": 10, "costUSD": 0.1},
                               "haiku": {"inputTokens": 2, "costUSD": 0.01}}}
        result = dispatch.normalize(body, "claude-code", "sonnet", "low", "t", "p", 1)
        self.assertEqual(len(result["entries"]), 2)
        self.assertEqual(sum(e["metrics"]["input_tokens"]["value"] for e in result["entries"]), 12)
        self.assertTrue(all(e["scope"] == "own_call" for e in result["entries"]))

    def test_missing_usage_and_model_remain_unknown(self):
        result = dispatch.normalize({"text": "hello"}, "grok", "alias", "low", "t", "p", 1)
        self.assertEqual(result["models_reported"], ["unresolved:alias"])
        self.assertIsNone(result["entries"][0]["metrics"]["estimated_api_cost"]["value"])

    def test_provider_error_not_success_even_with_answer(self):
        result = dispatch.normalize({"result": "partial", "subtype": "error_max_turns"},
                                    "claude-code", "sonnet", "low", "t", "p", 1)
        self.assertTrue(result["provider_failed"])

    def test_single_model_reasoning_is_recorded_without_adding_to_output(self):
        result = dispatch.normalize({"text": "ok", "usage": {"reasoning_tokens": 8},
            "modelUsage": {"grok": {"inputTokens": 10, "outputTokens": 12}}},
            "grok", "grok", "low", "t", "p", 1)
        metrics = result["entries"][0]["metrics"]
        self.assertEqual(metrics["reasoning_tokens"]["value"], 8)
        self.assertEqual(metrics["output_tokens"]["value"], 12)

    def run_fixture(self, root, stdout, returncode=0, timeout=False):
        root = Path(root)
        exe, prompt = root / "agent.exe", root / "prompt.txt"
        exe.touch()
        prompt.write_text("Review this text.", encoding="utf-8")
        args = argparse.Namespace(executable=exe, workspace=root, prompt_file=prompt,
            output_dir=root / "result", adapter="claude-code", model="sonnet", effort="low",
            pool="test-pool", task_id="t", timeout=1)
        process = Mock(pid=12345, returncode=returncode)
        if timeout:
            process.communicate.side_effect = [subprocess.TimeoutExpired("agent", 1), (stdout, b"")]
        else:
            process.communicate.return_value = (stdout, b"")
        with patch.object(dispatch.subprocess, "Popen", return_value=process) as start:
            with patch.object(dispatch.subprocess, "run"):
                result = dispatch.run(args)
        self.assertNotIn("shell", start.call_args.kwargs)
        return result, args

    def test_run_saves_result_and_usage_but_does_not_accept(self):
        with tempfile.TemporaryDirectory() as root:
            result, args = self.run_fixture(root, b'{"result":"done","usage":{"input_tokens":4}}')
            self.assertEqual(result["status"], "returned")
            self.assertEqual(result["acceptance"], "not_determined")
            self.assertEqual((args.output_dir / "answer.txt").read_text(), "done")
            self.assertTrue((args.output_dir / "usage.json").is_file())
            with self.assertRaises(FileExistsError):
                dispatch.run(args)

    def test_nonzero_exit_and_unparsed_response(self):
        for stdout, code, status in [(b'{"text":"passed"}', 1, "failed"),
                                      (b'not json', 0, "unparsed_response")]:
            with tempfile.TemporaryDirectory() as root:
                result, args = self.run_fixture(root, stdout, code)
                self.assertEqual(result["status"], status)
                self.assertTrue((args.output_dir / "stdout.json").is_file())

    def test_timeout_never_becomes_success_or_retries(self):
        with tempfile.TemporaryDirectory() as root:
            result, _ = self.run_fixture(root, b'{"result":"late reply"}', timeout=True)
            self.assertEqual(result["status"], "timed_out")
            self.assertFalse(result["automatic_retry"])


if __name__ == "__main__":
    unittest.main()
