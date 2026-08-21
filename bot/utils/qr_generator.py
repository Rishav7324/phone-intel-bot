"""QR Code and vCard contact generation utilities."""

import io
import qrcode
from bot.services.providers.base import PhoneMetadata


def generate_contact_qr(phone_number: str, label: str = "Phone Intel") -> io.BytesIO:
    """Generate a QR code PNG image containing a tel: URI."""
    clean_num = phone_number.strip()
    tel_uri = f"tel:{clean_num}"

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=2,
    )
    qr.add_data(tel_uri)
    qr.make(fit=True)

    img = qr.make_image(fill_color="#1E293B", back_color="#FFFFFF")
    bio = io.BytesIO()
    img.save(bio, format="PNG")
    bio.seek(0)
    bio.name = f"qr_{clean_num.replace('+', '')}.png"
    return bio


def generate_vcard(metadata: PhoneMetadata) -> io.BytesIO:
    """Generate an RFC 6350 compliant vCard (.vcf) contact file."""
    country = metadata.country_name if metadata.country_name != "Not available" else "Unknown"
    num = metadata.e164_format or metadata.international_format or metadata.input_number
    display_title = f"{metadata.flag_emoji} {country} {metadata.number_type}"

    vcard_text = (
        "BEGIN:VCARD\n"
        "VERSION:3.0\n"
        f"FN:{display_title}\n"
        f"ORG:Phone Intelligence Lookup\n"
        f"TEL;TYPE=CELL,VOICE:{num}\n"
        f"NOTE:Country: {country} | Type: {metadata.number_type} | Carrier: {metadata.carrier}\n"
        "END:VCARD\n"
    )

    bio = io.BytesIO(vcard_text.encode("utf-8"))
    bio.name = f"contact_{num.replace('+', '')}.vcf"
    bio.seek(0)
    return bio
