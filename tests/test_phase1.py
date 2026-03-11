import sys
import unittest


sys.path.append("d:/sem6_mini_project/velocity-os")


from brain.cortex.symbolic import SymbolicLayer
from brain.cortex.processor import CortexProcessor
from brain.senses.ui_parser import StructuralLayer
from brain.senses.vision import VisualLayer


class TestPhase1Modules(unittest.TestCase):
    def test_symbolic_cluster_match(self):
        symbolic = SymbolicLayer()
        result = symbolic.try_symbolic("play spotify")
        self.assertIsNotNone(result)
        self.assertEqual(result.get("method"), "symbolic")
        self.assertEqual(result.get("skill_id"), "spotify_play_pause")

    def test_symbolic_cluster_variant(self):
        symbolic = SymbolicLayer()
        result = symbolic.try_symbolic("start spotify")
        self.assertIsNotNone(result)
        self.assertEqual(result.get("skill_id"), "spotify_play_pause")

    def test_processor_predict_layer_order(self):
        processor = CortexProcessor()
        order_figma = processor._predict_layer_order("find", app="Figma")
        self.assertEqual(order_figma[0][0], "visual")

        order_chrome = processor._predict_layer_order("new tab", app="Chrome")
        self.assertEqual(order_chrome[0][0], "symbolic")

    def test_structural_try_structural_no_crash(self):
        structural = StructuralLayer()
        try:
            _ = structural.try_structural("Save", window_name="Notepad")
        except Exception as exc:
            self.fail(f"Structural layer raised exception: {exc}")

    def test_visual_try_visual_no_crash(self):
        visual = VisualLayer()
        try:
            _ = visual.try_visual("play")
        except Exception as exc:
            self.fail(f"Visual layer raised exception: {exc}")


if __name__ == "__main__":
    unittest.main()