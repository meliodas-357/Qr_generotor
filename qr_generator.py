import qrcode

print("QR code Generator")

data = ""
while not data.strip():
    data = input('Enter the text or URL: ')
    if not data.strip():
        print("Input can't be empty. Try again.")

print('Your Data:', data)

qr = qrcode.QRCode(version=None, box_size=10, border=4)
qr.add_data(data)
qr.make(fit=True)

colors = {
    1: "red", 2: "blue", 3: "green", 4: "yellow", 5: "orange",
    6: "purple", 7: "pink", 8: "brown", 9: "black", 10: "white"
}

print("\n".join(f"{k}: {v}" for k, v in colors.items()))

choice = None
while choice not in colors:
    try:
        choice = int(input("Enter the choice of your color of your QR code: "))
    except ValueError:
        pass

color = colors[choice]
img = qr.make_image(fill_color=color, back_color="white")

name = input("Enter your QR code name: ").strip()
if not name.lower().endswith((".jpg", ".jpeg", ".png")):
    name += ".png"

img.save(name)
print(f"Done! Saved to {name}")
