from django.test import SimpleTestCase

from board.sanitizers import sanitize_post_body


class PostBodySanitizerTests(SimpleTestCase):
    def test_removes_script_tags_event_handlers_and_unsafe_links(self):
        html = (
            '<p>Keep <strong>formatting</strong></p>'
            '<script>alert("xss")</script>'
            '<img src="/media/avatar.png" onerror="alert(1)">'
            '<a href="javascript:alert(1)">unsafe link</a>'
        )

        result = sanitize_post_body(html)

        self.assertIn("<strong>formatting</strong>", result)
        self.assertIn('src="/media/avatar.png"', result)
        self.assertNotIn("<script", result.lower())
        self.assertNotIn("onerror", result.lower())
        self.assertNotIn("javascript:", result.lower())
        self.assertNotIn('alert("xss")', result)

    def test_allows_trusted_video_embeds_and_removes_untrusted_sources(self):
        trusted = sanitize_post_body(
            '<iframe src="https://www.youtube.com/embed/abc123" '
            'onload="alert(1)" allowfullscreen></iframe>'
        )
        untrusted = sanitize_post_body(
            '<iframe src="https://evil.example/embed/abc123" '
            'onload="alert(1)"></iframe>'
        )

        self.assertIn('src="https://www.youtube.com/embed/abc123"', trusted)
        self.assertNotIn("onload", trusted.lower())
        self.assertNotIn("https://evil.example", untrusted)
        self.assertNotIn("onload", untrusted.lower())
