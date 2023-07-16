# D:/PetaKabar/whowherewhen/64_all_tagged_kecelakaan_17.pkl
import joblib

conc = []

a = joblib.load('D:/PetaKabar/whowherewhen/64_all_tagged_kecelakaan_17.pkl')
b = joblib.load('D:/PetaKabar/whowherewhen/32_all_tagged_kecelakaan_35.pkl')
c = joblib.load('D:/PetaKabar/whowherewhen/32_all_tagged_kecelakaan_36.pkl')

# for i in range(len(a)):
#     conc.append(a[i])

# for i in range(len(b)):
#     conc.append(b[i])

# for i in range(len(c)):
#     conc.append(c[i])

conc = joblib.load('D:/PetaKabar/whowherewhen/all_tagged_kecelakaan_9.pkl')
print((conc[112]))
print('*'*40)
print((conc[113]))
print('*'*40)
print((conc[111]))