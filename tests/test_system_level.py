import sys
import unittest


sys.path.append("d:/sem6_mini_project/velocity-os")


from brain.cortex.processor import CortexProcessor


class TestSystemLevel(unittest.TestCase):
    def test_end_to_end_symbolic_path(self):
        processor = CortexProcessor()
        result = processor.execute_with_fallback("play spotify", context={"app": "Spotify"})
        self.assertTrue(result.get("success", False))
        self.assertEqual(result.get("method_used"), "symbolic")
        self.assertEqual(result.get("skill_id"), "spotify_play_pause")

    def test_end_to_end_unknown_intent(self):
        processor = CortexProcessor()
        result = processor.execute_with_fallback("do something unknown", context={"app": "UnknownApp"})
        self.assertFalse(result.get("success", True))
        self.assertEqual(result.get("action"), "request_demonstration")
        self.assertIn("Please show me", result.get("message", ""))

    def test_end_to_end_predicted_layer_order(self):
        processor = CortexProcessor()
        order_figma = processor._predict_layer_order("find", app="Figma")
        self.assertEqual(order_figma[0][0], "visual")

        order_chrome = processor._predict_layer_order("new tab", app="Chrome")
        self.assertEqual(order_chrome[0][0], "symbolic")


if __name__ == "__main__":
    unittest.main()