"""Field-based rendering for Basic, Cloze and native/legacy image occlusion."""
from __future__ import annotations

import html
import math
import re
import struct
from html.parser import HTMLParser


class StudylistCleaner(HTMLParser):
    studylist_blocked = {'script', 'style', 'iframe', 'object', 'embed', 'template', 'noscript', 'head', 'form'}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.studylist_out = []
        self.studylist_stack = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        style = attrs.get('style', '')
        hidden = ('hidden' in attrs or attrs.get('aria-hidden') == 'true' or
                  re.search(r'(?:display\s*:\s*none|visibility\s*:\s*hidden)', style, re.I))
        blocked = bool(self.studylist_stack and self.studylist_stack[-1][1]) or tag in self.studylist_blocked or bool(hidden)
        if tag not in {'br', 'hr', 'img', 'input', 'meta', 'link', 'source', 'wbr', 'area', 'base', 'embed'}:
            self.studylist_stack.append((tag, blocked))
        if blocked:
            return
        safe = []
        for key, value in attrs.items():
            if key.lower().startswith('on') or key in {'srcdoc', 'formaction', 'hidden'}:
                continue
            if value is not None and re.match(r'\s*javascript:', value, re.I):
                continue
            if key == 'style':
                value = re.sub(r'(?:width|height|min-width|position)\s*:[^;]+;?', '', value or '', flags=re.I)
            safe.append(key if value is None else key + '="' + html.escape(value, quote=True) + '"')
        self.studylist_out.append('<' + tag + (' ' + ' '.join(safe) if safe else '') + '>')

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_endtag(self, tag):
        blocked = bool(self.studylist_stack and self.studylist_stack[-1][1])
        for i in range(len(self.studylist_stack)-1, -1, -1):
            if self.studylist_stack[i][0] == tag:
                blocked = self.studylist_stack[i][1]
                del self.studylist_stack[i:]
                break
        if not blocked and tag not in self.studylist_blocked:
            self.studylist_out.append('</' + tag + '>')

    def handle_data(self, data):
        if not self.studylist_stack or not self.studylist_stack[-1][1]:
            self.studylist_out.append(html.escape(data, quote=False))


def studylist_clean(value):
    value = re.sub(r'\[sound:[^\]]+\]', '', value or '')
    # Metadata and template directives are never useful field content.
    value = re.sub(r'\{\{[^{}]*image-occlusion:[^{}]*\}\}', '', value, flags=re.I)
    value = re.sub(r'image-occlusion:[^<\n{}]*', '', value, flags=re.I)
    value = re.sub(r'\{\{[^{}]+\}\}', '', value)
    # Some pasted fields contain escaped HTML source instead of actual markup.
    if re.search(r'&lt;/?(?:script|div|span|p|br|img|strong|b)\b', value, re.I):
        value = html.unescape(value)
    parser = StudylistCleaner()
    parser.feed(value)
    parser.close()
    return ''.join(parser.studylist_out)


def studylist_cloze_parts(value):
    """Return text and cloze nodes, preserving source order and nested answers."""
    parts, pos = [], 0
    for _ in range(len(value)+1):
        match = re.search(r'\{\{c(\d+)::', value[pos:], re.I)
        if not match:
            parts.append(value[pos:])
            break
        start, body_start = pos+match.start(), pos+match.end()
        parts.append(value[pos:start])
        i, depth, hint = body_start, 1, None
        while i < len(value):
            if value[i:i+2] == '{{':
                depth += 1; i += 2
            elif value[i:i+2] == '}}':
                depth -= 1
                if depth == 0:
                    break
                i += 2
            elif value[i:i+2] == '::' and depth == 1 and hint is None:
                hint = i; i += 2
            else:
                i += 1
        if depth:
            parts.append(value[start:]); break
        body = value[body_start:hint if hint is not None else i]
        parts.append((int(match[1]), studylist_cloze_parts(body)))
        pos = i+2
    return parts


def studylist_reveal_parts(parts, bold=False):
    output = []
    for part in parts:
        if isinstance(part, str):
            output.append(part)
        else:
            body = studylist_reveal_parts(part[1], bold)
            output.append('<strong class="studylist_answer">' + body + '</strong>' if bold else body)
    return ''.join(output)


def studylist_answers(parts, ordinal=None):
    answers = []
    for part in parts:
        if not isinstance(part, str):
            if ordinal is None or part[0] == ordinal:
                answer = studylist_clean(studylist_reveal_parts(part[1]))
                if answer.strip():
                    answers.append(answer)
            # Nested deletions remain separately testable; retain source order.
            answers.extend(studylist_answers(part[1], ordinal))
    return answers


def studylist_is_basic(model):
    """Stock Basic families, including renamed/localized stock models."""
    names = [f['name'].casefold() for f in model.get('flds', [])]
    return (model.get('type', 0) != 1 and
            (model.get('originalStockKind') in (0, 1, 2, 3) or
             ('front' in names and 'back' in names and model.get('name', '').casefold().startswith('basic'))))


def studylist_basic_fields(model):
    names = [f['name'] for f in model.get('flds', [])]
    front = next((i for i, name in enumerate(names) if name.casefold() == 'front'), 0)
    back = next((i for i, name in enumerate(names) if name.casefold() == 'back'), min(1, len(names)-1))
    return front, back


class StudylistLength(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.text = []
    def handle_data(self, data):
        self.text.append(data)


def studylist_visible_length(value):
    parser = StudylistLength()
    parser.feed(studylist_clean(value))
    return len(re.sub(r'\s+', ' ', ' '.join(parser.text)).strip())


def studylist_blanked_cloze(parts, blank, ordinal=None):
    """Blank this card's cN only, or all outer clozes in merged note mode."""
    answers = []

    def walk(nodes):
        output = []
        for part in nodes:
            if isinstance(part, str):
                output.append(part)
            elif ordinal is None or part[0] == ordinal:
                # An active outer deletion covers its nested deletions.
                answers.append(studylist_clean(studylist_reveal_parts(part[1])))
                output.append(len(answers))
            else:
                # Other cN answers are visible context. Recurse so a selected
                # deletion nested inside another cN can still be blanked.
                output.extend(walk(part[1]))
        return output

    output = walk(parts)
    numbered = len(answers) > 1
    terms = [(f'({i}) ' if numbered else '') + answer for i, answer in enumerate(answers, 1)]
    clue = ''.join(((f'({p}) ' if numbered else '') + html.escape(blank))
                   if isinstance(p, int) else p for p in output)
    return '<br>'.join(terms), studylist_clean(clue)


def studylist_is_io(fields, model):
    names = [f['name'].casefold() for f in model.get('flds', [])]
    return (model.get('originalStockKind') == 6 or any('image-occlusion:' in f for f in fields)
            or ('image' in names and any('mask' in n or 'occlusion' in n for n in names)))


def studylist_role(fields, model, role, aliases=(), fallback=None):
    for i, field in enumerate(model.get('flds', [])):
        if field.get('tag') == role and model.get('originalStockKind') == 6:
            return fields[i]
    aliases = {a.casefold() for a in aliases}
    for i, field in enumerate(model.get('flds', [])):
        if field['name'].casefold() in aliases:
            return fields[i]
    return fields[fallback] if fallback is not None and len(fields) > fallback else ''


def studylist_image_size(data):
    if data[:8] == b'\x89PNG\r\n\x1a\n' and len(data) > 24:
        return struct.unpack('>II', data[16:24])
    if data[:3] in (b'GIF',) and len(data) > 10:
        return struct.unpack('<HH', data[6:10])
    if data[:2] == b'\xff\xd8':
        i = 2
        while i+9 < len(data):
            if data[i] != 255:
                i += 1; continue
            marker = data[i+1]; i += 2
            if marker in (0xD8, 0xD9):
                continue
            length = int.from_bytes(data[i:i+2], 'big')
            if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                height, width = struct.unpack('>HH', data[i+3:i+7])
                return width, height
            i += max(length, 2)
    return 1000, 1000


def studylist_raw_shapes(value):
    shapes = []
    for match in re.finditer(r'\{\{c(\d+)::image-occlusion:([^{}]+)\}\}', html.unescape(value), re.I):
        segments = match[2].split(':')
        props = dict(s.split('=', 1) for s in segments[1:] if '=' in s)
        shapes.append({'kind': segments[0], 'ordinal': int(match[1]), 'props': props})
    return shapes


def studylist_io(fields, model, ordinal=None, native=None):
    occlusion = studylist_role(fields, model, 0, ('Occlusion', 'Occlusions'), 0)
    image = studylist_clean(studylist_role(fields, model, 1, ('Image', 'Picture'), 1))
    header = studylist_clean(studylist_role(fields, model, 2, ('Header', 'Title', 'Label')))
    extra = studylist_clean(studylist_role(fields, model, 3, ('Back Extra', 'Answer', 'Answer Labels', 'Extra 1')))
    legacy_question = studylist_clean(studylist_role(fields, model, -1, ('Question Mask', 'Question Mask SVG')))
    shapes = studylist_raw_shapes(occlusion)
    width, height = 1000, 1000
    if native is not None:
        width, height = studylist_image_size(native.image_data)
        # Anki 23.10 groups lack ordinal; retain source cloze ordinals there.
        if all(hasattr(g, 'ordinal') for g in native.occlusions):
            shapes = [{'kind': s.shape, 'ordinal': g.ordinal, 'props': {p.name:p.value for p in s.properties}}
                      for g in native.occlusions for s in g.shapes]
    width, height = max(1, width), max(1, height)
    def num(props, key, default=0):
        try:
            value = float(props.get(key, default))
            return value if math.isfinite(value) else default
        except (ValueError, TypeError):
            return default
    masks, labels = [], []
    for shape in shapes:
        props, kind = shape['props'], shape['kind']
        x, y = num(props, 'left')*width, num(props, 'top')*height
        angle = num(props, 'angle')*360/10000
        transform = f' transform="rotate({angle:g} {x:g} {y:g})"' if angle else ''
        style = ' fill="var(--studylist-mask,#c7c9ce)" stroke="var(--studylist-mask-border,#757b85)" stroke-width="1"'
        if kind == 'text':
            text = html.escape(props.get('text', ''))
            labels.append('<div class="studylist_io_label">'+text+'</div>')
            continue
        if ordinal is not None and shape['ordinal'] not in (0, ordinal) and props.get('oi') != '1':
            continue
        if kind == 'rect':
            masks.append(f'<rect x="{x:g}" y="{y:g}" width="{num(props,"width")*width:g}" height="{num(props,"height")*height:g}"{style}{transform}/>')
        elif kind == 'ellipse':
            rx, ry = num(props,'rx')*width, num(props,'ry')*height
            masks.append(f'<ellipse cx="{x+rx:g}" cy="{y+ry:g}" rx="{rx:g}" ry="{ry:g}"{style}{transform}/>')
        elif kind == 'polygon':
            points = []
            for point in props.get('points', '').split():
                try:
                    px, py = map(float, point.split(','))
                    if math.isfinite(px) and math.isfinite(py):
                        points.append((px,py))
                except (ValueError, TypeError):
                    pass
            if points:
                min_x,min_y=min(p[0] for p in points),min(p[1] for p in points)
                vertices=' '.join(f'{x+(px-min_x)*width:g},{y+(py-min_y)*height:g}' for px,py in points)
                masks.append('<polygon points="'+vertices+'"'+style+transform+'/>')
    def picture(overlay):
        if not image:
            return '<p>No image field found. Use Field mapping or edit this note.</p>'
        return ('<div class="studylist_io_image">' + image +
                f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" preserveAspectRatio="none">' + overlay + '</svg></div>')
    # The header is the question prompt: retain it before and after Reveal,
    # including in the full-screen viewer. Answer extras remain reveal-only.
    prompt = '<div class="studylist_io_header">'+header+'</div>' if header else ''
    term = prompt + picture('')
    if labels:
        term += '<div class="studylist_io_extra">'+''.join(labels)+'</div>'
    if extra:
        term += '<div class="studylist_io_extra">'+extra+'</div>'
    if legacy_question:
        definition = '<div class="studylist_io_image">'+image+'<div class="studylist_io_legacy">'+legacy_question+'</div></div>'
    else:
        definition = picture(''.join(masks))
    return term, prompt + definition


def studylist_render(fields, model, ordinal, mappings, per_note=True, native=None,
                     blank='_____________', swap=False):
    if studylist_is_io(fields, model):
        # Both note/card modes use every mask; the left image is always revealed.
        return studylist_io(fields, model, None, native)
    names = [f['name'] for f in model['flds']]
    if not fields:
        return '', ''
    mapping = mappings.get(str(model['id']), {})
    ti = names.index(mapping['studylist_term']) if mapping.get('studylist_term') in names else 0
    di = names.index(mapping['studylist_definition']) if mapping.get('studylist_definition') in names else min(1, len(fields)-1)
    term, definition = fields[ti], fields[di]
    if model.get('type') == 1:
        if not re.search(r'\{\{c\d+::', term, re.I):
            term = next((f for f in fields if re.search(r'\{\{c\d+::', f, re.I)), term)
        if blank not in ('_____________', '[...]', '{ }'):
            blank = '_____________'
        # Card ordinals are zero-based; cloze IDs in note fields start at c1.
        return studylist_blanked_cloze(studylist_cloze_parts(term), blank,
                                       None if per_note else ordinal + 1)
    if studylist_is_basic(model):
        fi, bi = studylist_basic_fields(model)
        choice = mapping.get('studylist_basic_term', 'auto')
        if choice == names[fi]:
            ti, di = fi, bi
        elif choice == names[bi]:
            ti, di = bi, fi
        else:
            # Back wins ties: it is the answer field in standard Basic notes.
            ti, di = (fi, bi) if studylist_visible_length(fields[fi]) < studylist_visible_length(fields[bi]) else (bi, fi)
        term, definition = fields[ti], fields[di]
    # Template/card ordinal never changes the selected answer/clue mapping.
    if swap:
        term, definition = definition, term
    return studylist_clean(term), studylist_clean(definition)
