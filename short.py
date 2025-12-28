import re

def extract_vcf_info(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split by VCARD entries
    vcards = re.split(r'END:VCARD', content, flags=re.IGNORECASE)
    filtered_vcards = []

    for vcard in vcards:
        if "BEGIN:VCARD" in vcard:
            lines = vcard.strip().splitlines()
            filtered_lines = []
            for line in lines:
                if line.startswith(("FN", "NOTE", "UID", "TEL", "PHOTO", "EMAIL")):

                    filtered_lines.append(line)

                    

            if filtered_lines:
                filtered_vcards.append("BEGIN:VCARD\nVERSION:3.0\n" + "\n".join(filtered_lines) + "\nEND:VCARD")

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(filtered_vcards))

# Example usage
extract_vcf_info('contacts_v3.vcf', 'contacts_v3_short.vcf')
