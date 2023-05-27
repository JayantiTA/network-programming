f = open('answer.log','r')
Lines = f.readlines()
count = 0
ans = []
for line in Lines:
    count += 1
    ans.append(line)
print("pesan EHLO: ",end="")
print(ans[0])
print("pesan yang menyatakan bahwa server mendukung TLS: ",end = "")
print (ans[6])
print("pesan yang menyatakan server siap mengirim email: ",end = "")
print(ans[15])
print("pesan yang menunjukkan username yang sudah di-hash: ",end = "")
print(ans[28])
print("pesan balasan server dari sebuah hello message dari client: ",end = "")
print(ans[1])
print("pesan bahwa koneksi telah ditutup : ",end = "")
print(ans[48])