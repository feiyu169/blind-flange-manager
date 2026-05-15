"""二维码工具"""

import io

import qrcode
from fastapi.responses import StreamingResponse


def generate_qrcode(data: str) -> StreamingResponse:
    """生成二维码图片"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    output = io.BytesIO()
    img.save(output, format="PNG")
    output.seek(0)

    return StreamingResponse(
        io.BytesIO(output.read()),
        media_type="image/png",
        headers={"Content-Disposition": f"attachment; filename=qrcode.png"},
    )
