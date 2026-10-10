from urllib.parse import urlsplit

import nh3


_ALLOWED_TAGS = {
    "a", "blockquote", "br", "caption", "code", "dd", "div", "dl", "dt",
    "em", "figcaption", "figure", "h1", "h2", "h3", "h4", "h5", "h6",
    "hr", "i", "iframe", "img", "li", "ol", "p", "pre", "s", "source",
    "span", "strong", "sub", "sup", "table", "tbody", "td", "th", "thead",
    "tr", "u", "ul", "video",
}

_ALLOWED_ATTRIBUTES = {
    "a": {"href", "title", "target"},
    "figure": {"align"},
    "iframe": {"src", "title", "width", "height", "allowfullscreen", "loading"},
    "img": {"src", "alt", "title", "width", "height"},
    "li": {"value"},
    "ol": {"start", "type"},
    "source": {"src", "type"},
    "table": {"summary"},
    "td": {"colspan", "rowspan"},
    "th": {"colspan", "rowspan", "scope"},
    "video": {"src", "controls", "poster", "preload", "width", "height", "loop", "muted"},
}

_ALLOWED_CLASSES = {
    "figure": {
        "image", "image_resized", "image-style-side", "image-style-align-left",
        "image-style-align-right", "image-style-align-center",
        "image-style-block-align-left", "image-style-block-align-right",
        "table", "media",
    },
    "img": {"image_resized"},
}


def _filter_attribute(tag, attribute, value):
    if tag != "iframe" or attribute != "src":
        return value

    parsed = urlsplit(value)
    if parsed.scheme != "https" or parsed.hostname is None:
        return None

    if parsed.hostname in {"www.youtube.com", "www.youtube-nocookie.com"}:
        return value if parsed.path.startswith("/embed/") else None

    if parsed.hostname == "player.vimeo.com":
        return value if parsed.path.startswith("/video/") else None

    return None


POST_BODY_CLEANER = nh3.Cleaner(
    tags=_ALLOWED_TAGS,
    clean_content_tags={"script", "style", "object", "embed", "svg", "math"},
    attributes=_ALLOWED_ATTRIBUTES,
    attribute_filter=_filter_attribute,
    allowed_classes=_ALLOWED_CLASSES,
    url_schemes={"http", "https", "mailto"},
    url_relative="pass_through",
    link_rel="noopener noreferrer",
)


def sanitize_post_body(value):
    return POST_BODY_CLEANER.clean(value or "")
