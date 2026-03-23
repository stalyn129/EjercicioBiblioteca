import qrcode

def generar_qr(usuario_id):
    img = qrcode.make(f"USER:{usuario_id}")
    img.save(f"qr_usuario_{usuario_id}.png")