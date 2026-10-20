import unittest

from src.parser import (
    ImageSize,
    _parse_embed_params,
    _parse_size,
    _render_inline_images,
    extract_inline_image_refs,
    render_markdown_body,
)


class TestImageResize(unittest.TestCase):
    def test_parse_size_pixels(self):
        # Valid single dimensions
        self.assertEqual(_parse_size("500"), ImageSize(500.0, "px", None, None))
        self.assertEqual(_parse_size(" 500 "), ImageSize(500.0, "px", None, None))
        self.assertEqual(_parse_size("500px"), ImageSize(500.0, "px", None, None))

        # Valid width x height
        self.assertEqual(_parse_size("500x100"), ImageSize(500.0, "px", 100.0, "px"))
        self.assertEqual(_parse_size("500X100"), ImageSize(500.0, "px", 100.0, "px"))
        self.assertEqual(_parse_size(" 500 x 100 "), ImageSize(500.0, "px", 100.0, "px"))
        self.assertEqual(_parse_size("500px x 100px"), ImageSize(500.0, "px", 100.0, "px"))

    def test_parse_size_percentages(self):
        # Single percentage: 80%
        self.assertEqual(_parse_size("80%"), ImageSize(80.0, "%", None, None))
        self.assertEqual(_parse_size(" 80% "), ImageSize(80.0, "%", None, None))

        # Two percentages: 80%x90%, 100%x30%
        self.assertEqual(_parse_size("80%x90%"), ImageSize(80.0, "%", 90.0, "%"))
        self.assertEqual(_parse_size("80% x 90%"), ImageSize(80.0, "%", 90.0, "%"))
        self.assertEqual(_parse_size("100%x30%"), ImageSize(100.0, "%", 30.0, "%"))
        self.assertEqual(_parse_size("100% x 30%"), ImageSize(100.0, "%", 30.0, "%"))

        # Mixed dimensions
        self.assertEqual(_parse_size("80%x200"), ImageSize(80.0, "%", 200.0, "px"))
        self.assertEqual(_parse_size("80%x200px"), ImageSize(80.0, "%", 200.0, "px"))
        self.assertEqual(_parse_size("500x30%"), ImageSize(500.0, "px", 30.0, "%"))

    def test_parse_size_invalid(self):
        self.assertIsNone(_parse_size(None))
        self.assertIsNone(_parse_size(""))
        self.assertIsNone(_parse_size("0"))
        self.assertIsNone(_parse_size("0%"))
        self.assertIsNone(_parse_size("0x0"))
        self.assertIsNone(_parse_size("500x0"))
        self.assertIsNone(_parse_size("100%x0%"))
        self.assertIsNone(_parse_size("10x"))
        self.assertIsNone(_parse_size("abc"))
        self.assertIsNone(_parse_size("Figure 1: 500 ratings"))

    def test_parse_embed_params(self):
        # No params: ![[path]]
        self.assertEqual(_parse_embed_params(None), (None, None))

        # Caption only: ![[path|A caption]]
        self.assertEqual(_parse_embed_params("A caption"), ("A caption", None))

        # Size only: pixels
        self.assertEqual(
            _parse_embed_params("500"),
            (None, ImageSize(500.0, "px", None, None)),
        )
        self.assertEqual(
            _parse_embed_params("500x100"),
            (None, ImageSize(500.0, "px", 100.0, "px")),
        )

        # Size only: percentage
        self.assertEqual(
            _parse_embed_params("80%"),
            (None, ImageSize(80.0, "%", None, None)),
        )
        self.assertEqual(
            _parse_embed_params("100%x30%"),
            (None, ImageSize(100.0, "%", 30.0, "%")),
        )

        # Caption and size: pixels
        self.assertEqual(
            _parse_embed_params("Distribution plot|500"),
            ("Distribution plot", ImageSize(500.0, "px", None, None)),
        )
        self.assertEqual(
            _parse_embed_params("Distribution plot|500x100"),
            ("Distribution plot", ImageSize(500.0, "px", 100.0, "px")),
        )

        # Caption and size: percentage
        self.assertEqual(
            _parse_embed_params("Distribution plot|80%"),
            ("Distribution plot", ImageSize(80.0, "%", None, None)),
        )
        self.assertEqual(
            _parse_embed_params("Distribution plot|100%x30%"),
            ("Distribution plot", ImageSize(100.0, "%", 30.0, "%")),
        )

        # Empty caption and size
        self.assertEqual(
            _parse_embed_params("|80%"),
            (None, ImageSize(80.0, "%", None, None)),
        )
        self.assertEqual(
            _parse_embed_params("|100%x30%"),
            (None, ImageSize(100.0, "%", 30.0, "%")),
        )

        # Multiple pipes in caption: ![[path|Table 1 | Results|100%x30%]]
        self.assertEqual(
            _parse_embed_params("Table 1 | Results|100%x30%"),
            ("Table 1 | Results", ImageSize(100.0, "%", 30.0, "%")),
        )

    def test_extract_inline_image_refs(self):
        body = """
        ![[plot1.png]]
        ![[plot2.png|Caption]]
        ![[plot3.png|Caption|500]]
        ![[plot4.png|Caption|80%x90%]]
        ![[plot5.png|100%x30%]]
        ![[images/plot6.png||80%]]
        """
        refs = extract_inline_image_refs(body)
        self.assertIn("plot1.png", refs)
        self.assertIn("images/plot1.png", refs)
        self.assertIn("plot2.png", refs)
        self.assertIn("plot3.png", refs)
        self.assertIn("plot4.png", refs)
        self.assertIn("plot5.png", refs)
        self.assertIn("images/plot6.png", refs)
        self.assertIn("plot6.png", refs)

    def test_render_inline_images_default(self):
        body = "![[eda-plot.png|Distribution of ratings]]"
        image_map = {"eda-plot.png": ("images/eda-plot.webp", 1600, 800)}
        output = _render_inline_images(body, image_map=image_map)

        self.assertIn('<figure class="gallery-item">', output)
        self.assertNotIn('is-resized', output)
        self.assertIn('src="/assets/images/eda-plot.webp"', output)
        self.assertIn('alt="Distribution of ratings"', output)
        self.assertIn('width="1600"', output)
        self.assertIn('height="800"', output)
        self.assertIn('<figcaption>Distribution of ratings</figcaption>', output)

    def test_render_inline_images_pixels_width_only(self):
        body = "![[eda-plot.png|Distribution of ratings|500]]"
        image_map = {"eda-plot.png": ("images/eda-plot.webp", 1600, 800)}
        output = _render_inline_images(body, image_map=image_map)

        self.assertIn('<figure class="gallery-item is-resized">', output)
        self.assertIn('width="500"', output)
        self.assertIn('height="250"', output)
        self.assertIn('style="width: 500px; max-width: 100%; height: auto;"', output)
        self.assertIn('<figcaption>Distribution of ratings</figcaption>', output)

    def test_render_inline_images_pixels_width_and_height(self):
        body = "![[eda-plot.png|Distribution of ratings|500x100]]"
        image_map = {"eda-plot.png": ("images/eda-plot.webp", 1600, 800)}
        output = _render_inline_images(body, image_map=image_map)

        self.assertIn('<figure class="gallery-item is-resized">', output)
        self.assertIn('width="500"', output)
        self.assertIn('height="100"', output)
        self.assertIn('style="width: 500px; max-width: 100%; height: 100px;"', output)

    def test_render_inline_images_percentage_width_only(self):
        # 80%: sets width to 80% while retaining aspect ratio
        body = "![[eda-plot.png|Ratings Plot|80%]]"
        image_map = {"eda-plot.png": ("images/eda-plot.webp", 1600, 800)}
        output = _render_inline_images(body, image_map=image_map)

        self.assertIn('<figure class="gallery-item is-resized">', output)
        self.assertIn('style="width: 80%; max-width: 100%; height: auto;"', output)
        self.assertIn('width="1600"', output)
        self.assertIn('height="800"', output)
        self.assertIn('<figcaption>Ratings Plot</figcaption>', output)

    def test_render_inline_images_percentage_two_values(self):
        # 80%x90%: changes aspect ratio relative to percentages
        body = "![[eda-plot.png|Ratings Plot|80%x90%]]"
        image_map = {"eda-plot.png": ("images/eda-plot.webp", 1600, 800)}
        output = _render_inline_images(body, image_map=image_map)

        self.assertIn('<figure class="gallery-item is-resized">', output)
        self.assertIn('width="1280"', output)  # 1600 * 0.8
        self.assertIn('height="720"', output)  # 800 * 0.9
        # ratio = (1600 * 80) / (800 * 90) = 1.7778
        self.assertIn('aspect-ratio: 1.7778', output)
        self.assertIn('style="width: 80%; max-width: 100%; height: auto;', output)

    def test_render_inline_images_preserve_width_change_height(self):
        # 100%x30%: preserves 100% width, reduces height to 30%
        body = "![[eda-plot.png|Ratings Plot|100%x30%]]"
        image_map = {"eda-plot.png": ("images/eda-plot.webp", 1600, 800)}
        output = _render_inline_images(body, image_map=image_map)

        self.assertIn('<figure class="gallery-item is-resized">', output)
        self.assertIn('width="1600"', output)
        self.assertIn('height="240"', output)  # 800 * 0.3
        # ratio = (1600 * 100) / (800 * 30) = 6.6667
        self.assertIn('aspect-ratio: 6.6667', output)
        self.assertIn('style="width: 100%; max-width: 100%; height: auto;', output)

    def test_render_markdown_body_integration(self):
        md = "## Analysis\n\n![[photo.png|Chart|100%x30%]]\n\nDone."
        html_out = render_markdown_body(md)
        self.assertIn('<figure class="gallery-item is-resized">', html_out)
        self.assertIn('style="width: 100%; max-width: 100%; height: auto;', html_out)
        self.assertIn('aspect-ratio: 100 / 30', html_out)  # Fallback when image not in map
        self.assertIn('<figcaption>Chart</figcaption>', html_out)


if __name__ == "__main__":
    unittest.main()
