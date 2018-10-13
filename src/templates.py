def format_reservations(reservations):
    return "Reserved saunas:\n {}".format("\n".join(str(x) for x in reservations))


def format_timetable(topics, cal, state):
    state = ("Vapaa", "Varattu", "Oma varaus")
    column_width = max(len(x) for x in (*topics, *state))
    columns = len(topics)
    temp = f"{{:{column_width}}}" * columns
    rows = [temp.format(*topics)]
    for time, *items in cal:
        rows.append(temp.format(time, *(state[r[0]] for r in items)))

    final = "\n".join(rows)
    return final
