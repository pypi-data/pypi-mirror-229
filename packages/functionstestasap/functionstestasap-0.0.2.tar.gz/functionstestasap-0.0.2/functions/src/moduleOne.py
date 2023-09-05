from datetime import datetime
def test1():
    a = datetime.strptime('10:00:00', '%H:%M:%S').time()
    return a

def test2():
    b = 'Is this valid'
    return b