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
print('''
    1: "red",
    2: "blue",
    3: "green",
    4: "yellow",
    5: "orange",
    6: "purple",
    7: "pink",
    8: "brown",
    9: "black",
    10: "white"''')
choice = int(input("Enter the choice of your color of your QRcode : "))
colors = {
    1: "red",
    2: "blue",
    3: "green",
    4: "yellow",
    5: "orange",
    6: "purple",
    7: "pink",
    8: "brown",
    9: "black",
    10: "white"
}

color = colors[choice]

img = qr.make_image(fill_color=color, back_color="white")
name = input("Enter your QR code name :")
name = name + ".jpg"
img.save(name)

print("Done! Saved to qr.png")
