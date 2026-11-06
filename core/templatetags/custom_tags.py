import os
import re
from urllib.parse import urlsplit
from uuid import uuid4

from django import template
from django.conf import settings
from django.contrib.staticfiles import finders
from django.templatetags.static import static
from django.utils.html import escape, format_html, format_html_join
from django.utils.safestring import mark_safe
from django.utils.text import Truncator

register = template.Library()


@register.filter
def times(number):
    """
    Retourne une liste contenant number élements pour itérer
    """
    return range(number)


@register.filter
def dict_key(d, key):
    return d.get(key)


@register.simple_tag
def static_versioned(path):
    """
    Return a static URL with a file modification timestamp query string.
    This helps browsers pick up rebuilt assets without manual cache clearing.
    """
    resolved_path = finders.find(path)
    if not resolved_path:
        return static(path)

    version = int(os.path.getmtime(resolved_path))
    return f"{static(path)}?v={version}"


@register.filter
def stars(number):
    """
    Retourne un tuple (filled, empty) pour afficher les étoiles.
    filled = nombre d'étoiles remplies
    empty = nombre d'étoiles non remplies
    """
    filled = int(number)
    empty = 5 - filled
    return f"★" * filled + f"☆" * empty


@register.simple_tag
def difficulty_stars(number):
    difficulty = max(0, min(5, int(number)))
    icons = [
        ("bi-star-fill" if index < difficulty else "bi-star",)
        for index in range(5)
    ]
    rendered_icons = format_html_join(
        "",
        '<i class="bi {}" aria-hidden="true"></i>',
        icons,
    )
    return format_html(
        '<span class="difficulty-stars" role="img" aria-label="Difficulté {} sur 5">{}</span>',
        difficulty,
        rendered_icons,
    )


@register.filter
def statement_excerpt(value, word_count=25):
    text = re.sub(r"!\[[^\]\r\n]*\]\([^)\s]+\)", "Illustration", str(value))
    return Truncator(text).words(word_count)


@register.filter
def linebreaks_preserve_latex(value):
    """
    Convert newlines to <br> tags while preserving LaTeX math expressions.
    Protects both inline ($...$) and display ($$...$$) math from being mangled.
    Similar to Django's linebreaksbr but preserves LaTeX syntax.
    """
    if not value:
        return value

    images = {}
    media_prefix = (
        f"{urlsplit(settings.MEDIA_URL).path.rstrip('/')}/problem_statement_images/"
    )

    def save_image(match):
        image_url = urlsplit(match.group(2))
        filename = image_url.path.rsplit("/", 1)[-1]
        if (
            image_url.scheme
            or image_url.netloc
            or image_url.query
            or image_url.fragment
            or image_url.path != f"{media_prefix}{filename}"
            or not re.fullmatch(r"[0-9a-f]{32}\.webp", filename)
        ):
            return match.group(0)

        placeholder = f"__BC_IMAGE_{uuid4().hex}__"
        images[placeholder] = format_html(
            '<img class="problem-statement-image" src="{}" alt="{}" loading="lazy">',
            image_url.path,
            match.group(1),
        )
        return placeholder

    value = re.sub(r"!\[([^\]\r\n]*)\]\(([^)\s]+)\)", save_image, str(value))
    value = escape(value)

    # Protect display math ($$...$$) - must be done first
    display_math_blocks = []

    def save_display_math(match):
        display_math_blocks.append(match.group(0))
        placeholder = f"__DISPLAY_MATH_{len(display_math_blocks) - 1}__"
        return placeholder

    # Replace $$...$$ with placeholders
    value = re.sub(r"\$\$[\s\S]*?\$\$", save_display_math, value)

    # Protect inline math ($...$ but not $$)
    inline_math_blocks = []

    def save_inline_math(match):
        inline_math_blocks.append(match.group(0))
        placeholder = f"__INLINE_MATH_{len(inline_math_blocks) - 1}__"
        return placeholder

    # Match single $ ... $ (negative lookbehind/lookahead to avoid $$)
    value = re.sub(
        r"(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)", save_inline_math, value, flags=re.DOTALL
    )

    # Convert newlines to <br> in remaining content
    value = value.replace("\n", "<br>")

    # Restore display math
    for i, block in enumerate(display_math_blocks):
        value = value.replace(f"__DISPLAY_MATH_{i}__", block)

    # Restore inline math
    for i, block in enumerate(inline_math_blocks):
        value = value.replace(f"__INLINE_MATH_{i}__", block)

    for placeholder, image in images.items():
        value = value.replace(placeholder, str(image))

    return mark_safe(value)
