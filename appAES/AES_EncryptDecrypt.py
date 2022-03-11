from fractions import gcd

C1 = "3ae81964c8ecf1524b47c42cb0ecd2a3b6768dccd55960d7ff0a998f839b8c312a2cd821c270ae961777dd4dd50aa631fe823a8afd914911adf69c1c6cfda3b3aed01dad372cfdd6e9f63a4cc39e1a455cbfd04dea72bf07c4790d5fec469198ce28113d6d38a7baced9d3c3695ab27cbc5ab434aa8d2b5f53f66a383e079ddaed485d4a2b446e410eafcadbba9f159494c28c4a19fd416dff90f8c141e96d8260f8e6e0901832e31899c48ce0cbdae6a24595a19a01e490c87e7b48860e09006920d8ef7384217358c6db90638d6e8cbc795a091240f24105d8f3b27fe4b98fe9a507e00590b4cded41777b1b8967b0f752231e0e856b8f0132bde30a6e082e"
C2 = "391e0340e5931a202012572ddacad877e5af3a1d846b70c1e64e3041f9ac0a3c7e8f82621df908eadca44fe777a6b1c799610be829e13ca233982fd268034addb5a79fa19f984631fdf3a61d32fc75ed77176c7a0b719504e804076dca66f10111aa124a7efe743ada75dda2ec53f3c28882a7724928685918261739f960a3648aa3eadc426181aa146a8ba0ff20f1c53de2113e0196af09595dc2ad1a0fe12096ff681f61363044615a7f72edf1f8c6531055e66c1e5f4498434c731d2308fecae46c779379ea3d7d7a5f1c2a0efeb5bc1b8a4af4fb21fce1dae943c27043e86642b3b1e6b889a31e7c4bc01bc2ebae4dc8432344532567d1d3df8b9bcafcbf"

n = "00e85242770a66698c6449615ad48f70e5ff7f49ca4533437d85367e1af38f31aa35948eb33f9788f7164a1dd5c3875bf86b693bd8cc82e2cbcbd01cf7d1b451ef67cb7290fa790ee10224e3725b37b6bc3d5356da9d0fbac1e06bb26ff24303d906d3c966c81b199a78b9ef022b0fb928e582fc0ce02957f6b1642101f92e834aab47249ee408c291d3fce872c14469123137f4da492800750336472069f4e24b4a0e3ee51585ae786843a3c03961c212a1e394d271e82614c4e7aa1d5da416011f9b4081a8e47065751adede51d09097fb8a41acbe2e545cb6d404401d5916c3f68616e96679b35f7774a9e442b1987414b022ee06f00fac3dddb6141943e553"

C1int = int(C1, 16)
C2int = int(C2, 16)
subtract = C1int - C2int

print("C1-C2 : ")
print(subtract)

n_int = int(n,16)

p = gcd(n_int , subtract)

print("Hex value of p : ")
print(hex(p))

q = n_int/p

print("q = n/p : ")
print(q)

Phi_N = (p-1)*(q-1)

print("Phi(n) : ")
print(Phi_N)

def egcd(a, b):
    if a == 0:
        return (b, 0, 1)
    else:
        g, y, x = egcd(b % a, a)
        return (g, x - (b // a) * y, y)

def modinv(a, m):
    g, x, y = egcd(a, m)
    if g != 1:
        raise Exception('modular inverse does not exist')
    else:
        return x % m

e = 65537
d = modinv(e, Phi_N)
print("d : ")
print(d)













