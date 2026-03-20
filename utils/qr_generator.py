import qrcode

def generate_qr(token: str) -> str:
    file_path = f"qr_{token}.png"
    img = qrcode.make(f"coffee:{token}")
    img.save(file_path)
    return file_path