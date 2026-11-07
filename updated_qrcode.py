import qrcode

COLORS = {
    1: "red", 2: "blue", 3: "green", 4: "yellow", 5: "orange",
    6: "purple", 7: "pink", 8: "brown", 9: "black", 10: "white"
}


def get_required_input(prompt):
    value = ""
    while not value.strip():
        value = input(prompt)
        if not value.strip():
            print("Input can't be empty. Try again.")
    return value.strip()


def choose_color():
    print("\n".join(f"{k}: {v}" for k, v in COLORS.items()))

    choice = None
    while choice not in COLORS:
        try:
            choice = int(input("Enter the choice of your color of your QR code: "))
            if choice not in COLORS:
                print(f"Please choose a number between 1 and {len(COLORS)}.")
        except ValueError:
            print("Please enter a number, not letters.")

    return COLORS[choice]


def get_filename():
    name = input("Enter your QR code name: ").strip()
    if not name.lower().endswith((".jpg", ".jpeg", ".png")):
        name += ".png"
    return name


def generate_qr(data, color, filename):
    qr = qrcode.QRCode(version=None, box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color=color, back_color="white")
    img.save(filename)
    print(f"Done! Saved to {filename}")


def finish_qr(data):
    color = choose_color()
    filename = get_filename()
    generate_qr(data, color, filename)


def option_text_or_link():
    data = get_required_input("Enter the text or URL: ")
    print("Your Data:", data)
    finish_qr(data)


def option_contact_card():
    name = get_required_input("Enter the contact name: ")
    phone = input("Enter the phone number: ").strip()
    email = input("Enter the email address: ").strip()

    data = f"BEGIN:VCARD\nVERSION:3.0\nN:{name}\nTEL:{phone}\nEMAIL:{email}\nEND:VCARD"
    finish_qr(data)


def option_wifi():
    ssid = get_required_input("Enter the Wi-Fi name (SSID): ")
    password = input("Enter the Wi-Fi password: ").strip()
    security = input("Enter the security type (WPA/WEP/nopass) [WPA]: ").strip() or "WPA"

    data = f"WIFI:T:{security};S:{ssid};P:{password};;"
    finish_qr(data)


def main():
    print("QR code Generator")

    while True:
        print("\n1. link or text")
        print("2. contact card")
        print("3. wifi")
        print("4. exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            option_text_or_link()
        elif choice == "2":
            option_contact_card()
        elif choice == "3":
            option_wifi()
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1, 2, 3 or 4.")


if __name__ == "__main__":
    main()
