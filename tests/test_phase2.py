import sys
import unittest


sys.path.append("d:/sem6_mini_project/velocity-os")


from brain.cortex.learning import LearningEngine
from brain.cortex.temporal_context import TemporalContext
from brain.cortex.diagnostics import FailureDiagnostics
from brain.cortex.cross_layer import CrossLayerLearning
from brain.cortex.processor import CortexProcessor


class TestPhase2Modules(unittest.TestCase):
    def test_temporal_context(self):
        ctx = TemporalContext().get_context()
        self.assertIn("hour", ctx)
        self.assertIn("network_state", ctx)

    def test_learning_update_confidence(self):
        engine = LearningEngine()
        engine.update_confidence("spotify_play_pause", success=True)
        self.assertIn("spotify_play_pause", engine.skills)

    def test_diagnostics(self):
        diag = FailureDiagnostics()
        rec = diag.diagnose("element_not_found", "unknown_skill", {})
        self.assertIn("recommendations", rec)

    def test_cross_layer_store_and_get(self):
        cll = CrossLayerLearning()
        cll.store_visual_hint("spotify_play_pause", b"abc", 0.7)
        data = cll.get_visual_hint("spotify_play_pause", max_age_seconds=9999)
        self.assertEqual(data, b"abc")

    def test_processor_failure_diagnostic(self):
        processor = CortexProcessor()
        result = processor.execute_with_fallback("unknown task", context={"app": "Unknown"})
        self.assertFalse(result.get("success", True))
        self.assertIn("diagnostic", result)


if __name__ == "__main__":
    unittest.main()