ja_text_ranges = [
    (0x3041, 0x3096),   # Hiragana
    (0x30A0, 0x30FF),   # Katakana (Full Width)
    (0x3400, 0x4DB5),   # Kanji 1
    (0x4E00, 0x9FCB),   # Kanji 2
    (0xF900, 0xFA6A),   # Kanji 3
]

ja_non_text_ranges = [
    (0x2E80, 0x2FD5),   # Kanji Radicals
    (0xFF5F, 0xFF9F),   # Halfwidth Katakana and Punctuation
    (0x3000, 0x303F),   # Punctuation and Symbols
    (0xFF01, 0xFF5E),   # Fullwidth Alphanumerics and Punctuation
]

ja_ranges = ja_text_ranges + ja_non_text_ranges

def in_ranges(character, ranges):
    return any([start <= ord(character) <= end for start, end in ranges])

def is_ja_text(character):
    return in_ranges(character, ja_text_ranges)

def is_ja_non_text(character):
    return in_ranges(character, ja_non_text_ranges)

def is_ja(character):
    return in_ranges(character, ja_ranges)


# TODO: Preservr [sound:...] tags

def remove_syntax(text):

    ret = []

    segments = text.split(' ')

    was_seg_ja = False

    for i, segment in enumerate(segments):
        bracket_start_idx = segment.find('[')
        bracket_end_idx = -1
        if bracket_start_idx >= 0:
            bracket_end_idx = segment.find(']', bracket_start_idx+1)

        is_seg_ja = False
        out_seg = None

        if bracket_start_idx >= 0 and bracket_end_idx >= 0:
            text_pre = segment[:bracket_start_idx]
            text_post = segment[bracket_end_idx+1:]
            is_seg_ja = True
            out_seg = text_pre + text_post

        else:
            if len(segment) > 0:
                is_seg_ja = any([is_ja(c) for c in segment])
            else:
                is_seg_ja = was_seg_ja
            out_seg = segment

        if i > 0:
            if not was_seg_ja or not is_seg_ja:
                ret.append(' ')

        ret.append(out_seg)
        was_seg_ja = is_seg_ja

    return ''.join(ret)
