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
        
if __name__ == "__main__":
    print_raw("asd\n\n\u1234saddsadsaddas \u0000ssafaasfasfsa fsa \n\n asdasd dad ss ääåäåölåplq")