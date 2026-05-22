import re


LOG_PATTERN = re.compile(
    r"^(?P<timestamp>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s+"
    r"(?P<level>INFO|WARN|ERROR|DEBUG|TRACE)\s+"
    r"(?P<service>[\w\-\.]+)\s+"
    r"(?P<message>.*)$"
)


def parse_log_lines(log_text: str) -> list[dict]:
    parsed_lines = []

    for idx, line in enumerate(log_text.splitlines(), start=1):
        line = line.strip()

        if not line:
            continue

        match = LOG_PATTERN.match(line)

        if match:
            parsed_lines.append({
                "line_number": idx,
                "timestamp": match.group("timestamp"),
                "log_level": match.group("level"),
                "service": match.group("service"),
                "message": match.group("message"),
                "raw_line": line,
            })
        else:
            parsed_lines.append({
                "line_number": idx,
                "timestamp": None,
                "log_level": "UNKNOWN",
                "service": None,
                "message": line,
                "raw_line": line,
            })

    return parsed_lines

def build_log_chunks(parsed_lines: list[dict], window_size: int = 2) -> list[dict]:
    chunks = []

    for index, line in enumerate(parsed_lines):
        if line["log_level"] not in ["ERROR", "WARN"]:
            continue

        start_index = max(0, index - window_size)
        end_index = min(len(parsed_lines), index + window_size + 1)

        context_lines = parsed_lines[start_index:end_index]

        chunk_text = "\n".join(
            item["raw_line"] for item in context_lines
        )

        chunk = {
            "chunk_id": f"chunk-{line['line_number']}",
            "center_line": line["line_number"],
            "chunk_text": chunk_text,
            "line_start": context_lines[0]["line_number"],
            "line_end": context_lines[-1]["line_number"],
            "timestamp_start": context_lines[0]["timestamp"],
            "timestamp_end": context_lines[-1]["timestamp"],
            "log_level": line["log_level"],
            "service": line["service"],
        }

        chunks.append(chunk)

    return chunks