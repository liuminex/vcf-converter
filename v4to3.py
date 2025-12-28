import re

def v4_to_v3(v4_file, v3_file):
    with open(v4_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    v3_lines = []
    photo_data = ""
    in_photo = False

    for line in lines:
        line = line.rstrip()

        # Skip empty lines
        if not line:
            continue

        # BEGIN and END stay the same
        if line.startswith("BEGIN:VCARD"):
            v3_lines.append(line)
            continue
        if line.startswith("END:VCARD"):
            # Add any pending photo
            if photo_data:
                v3_lines.append(photo_data)
                photo_data = ""
                in_photo = False
            v3_lines.append(line)
            continue

        # Convert version
        if line.startswith("VERSION:4.0"):
            v3_lines.append("VERSION:3.0")
            continue

        # Convert FN/N lines (remove v4 attributes)
        if line.startswith("FN"):
            v3_lines.append(re.sub(r';.*?:', ':', line))
            continue
        if line.startswith("N"):
            v3_lines.append(line)
            continue

        # Convert TEL/ADR lines (remove v4 attributes)
        if line.startswith("TEL") or line.startswith("ADR"):
            # Remove any v4 attributes like TYPE or PREF but keep essential type
            line_v3 = re.sub(r';[^:]*', '', line.split(":",1)[0]) + ':' + line.split(":",1)[1]
            v3_lines.append(line_v3)
            continue

        # Keep BDAY, NOTE, URL as-is
        if line.startswith("BDAY") or line.startswith("NOTE") or line.startswith("URL"):
            v3_lines.append(line)
            continue

        # Handle PHOTO
        if line.startswith("PHOTO"):
            in_photo = True
            # Convert v4 PHOTO format to v3: PHOTO;ENCODING=b;TYPE=<type>:<data>
            match = re.match(r'PHOTO(;.*)?:(.*)', line)
            if match:
                attrs = match.group(1) or ""
                data = match.group(2)

                # Extract type from data URL if present
                m = re.match(r'data:image/(.*?);base64,', data)
                if m:
                    img_type = m.group(1).upper()
                    img_data = data.split(',',1)[1]
                    photo_data = f"PHOTO;ENCODING=b;TYPE={img_type}:{img_data}"
                else:
                    photo_data = line  # fallback if no data URL
            continue

        # Handle continuation lines (photo base64 split lines)
        if in_photo:
            if line.startswith(' '):  # continuation line
                photo_data += line.strip()
            else:
                # end of photo block
                v3_lines.append(photo_data)
                photo_data = ""
                in_photo = False
                v3_lines.append(line)

    # Write v3 output
    with open(v3_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(v3_lines))
    print(f"Converted {v4_file} to {v3_file}")

# Example usage
v4_to_v3("contacts_v4.vcf", "contacts_v3.vcf")
