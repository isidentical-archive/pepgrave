import sys
import token


def untokenize(stream_tokens):
    buffer = ""
    indents = []
    ws_offset = 0
    last_token = None
    indent_type = None
    first_indent = False
    waiting_to_be_indented = False

    for stream_token in stream_tokens:
        assert len(indents) >= 0

        if stream_token.type == token.ENDMARKER:
            break
        elif stream_token.type == token.INDENT:
            if not first_indent:
                indent_type = stream_token.string
                first_indent = True
            indents.append(indent_type)
        elif stream_token.type == token.DEDENT:
            indents.pop()

        if last_token and last_token.type not in {token.NEWLINE, token.NL}:
            ws_offset = stream_token.start[1] - last_token.end[1]
        else:
            waiting_to_be_indented = True

        if waiting_to_be_indented:
            if stream_token.type == token.DEDENT:
                last_token = stream_token
                ws_offset = 0
                continue
            else:
                buffer += "".join(indents)
                waiting_to_be_indented = False

        if ws_offset > 0:
            buffer += " " * ws_offset
            ws_offset = 0

        if stream_token.type == token.INDENT:
            pass
        else:
            buffer += stream_token.string

        last_token = stream_token

    return buffer
