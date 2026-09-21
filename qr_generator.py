import qrcode #this is qrcode library of built in function of python

print("QR code Generator")
#taking input from the user
data =  input('Enter the text or URL :')

#verifiing the data entered
print('Your Data : ',data)

qr = qrcode.QRCode(
    version= None,
    box_size = 10,
    border = 4)

qr.add_data(data)
qr.make(fit=True)

img = qr.make_image(fill_color="#FF0000", back_color="white")
img.save("redqr.png")

print("Done! Saved to qr.png")
