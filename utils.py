import datetime

def print_raw(text, width=50):
    uppers = ""
    lowers = ""
    
    for t in text:
        a = repr(t)[1:-1]
        b = hex(ord(t))[2:]
        pad = 5
        uppers += a.rjust(pad)
        lowers += b.rjust(pad)

    zipped_chunks = ((uppers[i:i + width], lowers[i:i + width]) for i in range(0, len(uppers), width))

    for t, i in zipped_chunks:
        print(t)
        print(i)
        print("-" * width)


def next_weekday(weekday, week=0, from_ = None):
    """
       next_weekday(6, week
    """
    now = datetime.datetime.now()
    diff = weekday - d.weekday()
    if diff < 0:
        diff = diff +7
    return  now + datetime.timedelta(days=days_ahead)

if __name__ == "__main__":
    print_raw("asd\n\n\u1234saddsadsaddas \u0000ssafaasfasfsa fsa \n\n asdasd dad ss ääåäåölåplq")