import unittest
from types import SimpleNamespace

from docling_batch.images import filter_markdown_image_refs, should_keep_picture


class ImageHeuristicTests(unittest.TestCase):
    def test_should_drop_small_captionless_footer_like_picture(self):
        doc = SimpleNamespace(
            pages={
                2: SimpleNamespace(
                    size=SimpleNamespace(width=595, height=842),
                )
            }
        )
        picture = SimpleNamespace(
            prov=[SimpleNamespace(page_no=2, bbox=SimpleNamespace(l=230, r=363, t=48, b=26))],
            captions=[],
        )

        self.assertFalse(should_keep_picture(doc, picture))

    def test_should_keep_large_picture_without_caption(self):
        doc = SimpleNamespace(
            pages={
                2: SimpleNamespace(
                    size=SimpleNamespace(width=595, height=842),
                )
            }
        )
        picture = SimpleNamespace(
            prov=[SimpleNamespace(page_no=2, bbox=SimpleNamespace(l=81, r=513, t=645, b=300))],
            captions=[],
        )

        self.assertTrue(should_keep_picture(doc, picture))

    def test_should_drop_small_qr_like_picture_without_caption(self):
        doc = SimpleNamespace(
            pages={
                1: SimpleNamespace(
                    size=SimpleNamespace(width=595, height=842),
                )
            }
        )
        picture = SimpleNamespace(
            prov=[SimpleNamespace(page_no=1, bbox=SimpleNamespace(l=469, r=540, t=154, b=89))],
            captions=[],
        )

        self.assertFalse(should_keep_picture(doc, picture))

    def test_filter_markdown_image_refs_removes_images_marked_false(self):
        markdown = "\n".join(
            [
                "before",
                "![Image](artifacts/image_1.png)",
                "middle",
                "![Image](artifacts/image_2.png)",
                "after",
            ]
        )

        filtered = filter_markdown_image_refs(markdown, [False, True])

        self.assertNotIn("image_1.png", filtered)
        self.assertIn("image_2.png", filtered)
