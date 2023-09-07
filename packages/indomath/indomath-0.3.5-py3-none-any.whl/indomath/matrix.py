def matriks2x2_kali(a,b,c,d,e,f,g,h):
    h1 = a * e + c * f
    h2 = b * e + d * f
    h3 =  a * g + a * h
    h4 = b * g  + d * h
    print(h1,h3)
    print(h2,h4)
def matriks2x2_tambah(a,b,c,d,e,f,g,h):
    print(a + e,c + g)
    print(b + d,d + h)
def matriks2x2_kurang(a,b,c,d,e,f,g,h):
    print(a - e,c - g)
    print(b - d,d - h)
def matriks2x2_skalar(a,b,c,d,nilai):
    print(nilai * a,nilai * c)
    print(nilai * b,nilai * c)
def matriks2x2_adjoint(a,b,c,d):
    print(d,c * -1)
    print(b * -1,a)
def matriks2x2_determinan(a,b,c,d):
    print(a * d - b * c)