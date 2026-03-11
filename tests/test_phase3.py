import sys
import unittest


sys.path.append("d:/sem6_mini_project/velocity-os")


from brain.cortex.observer import Observer
from brain.cortex.synthesizer import Synthesizer
from brain.cortex.composite_executor import CompositeExecutor


class TestPhase3Modules(unittest.TestCase):
    def test_observer_summary(self):
        obs = Observer()
        obs.is_recording = True
        obs.start_time = None
        obs.actions = [{"type": "click", "x": 1, "y": 2, "timestamp": 0.1}]
        summary = obs._build_summary()
        self.assertIn("actions", summary)
        self.assertEqual(summary["action_count"], 1)

    def test_synthesizer_format_actions(self):
        syn = Synthesizer()
        actions = [
            {"type": "click", "x": 1, "y": 2, "element": {"name": "OK"}},
            {"type": "key_press", "key": "a"},
        ]
        text = syn._format_actions(actions)
        self.assertIn("Clicked OK", text)
        self.assertIn("Pressed", text)

    def test_composite_executor(self):
        execu = CompositeExecutor()
        skill = {
            "steps": [
                {"action": "type_text", "text": "hello"},
                {"action": "unknown_action"},
            ]
        }
        result = execu.execute(skill)
        self.assertFalse(result["success"])
        self.assertEqual(result["steps_executed"], 2)


if __name__ == "__main__":
    unittest.main()
