def page_ranges(start, step, count):
    """`count` consecutive half-open ObjectID ranges of width `step`, starting at `start`."""
    return [(start + i * step, start + (i + 1) * step) for i in range(count)]
