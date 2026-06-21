import re

similarity_limit = 0.6

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
            n = ""
            fn = ""
            similarity = 0.0
            for line in lines:
                if line.startswith("FN"):
                    fn = line.split(":", 1)[1].strip().replace(";", " ")
                if line.startswith("N"):
                    n = line.split(":", 1)[1].strip().replace(";", " ")

                if fn != "" and n != "":
                    # if they are more than 70% similary, skip
                    fn_parts = fn.lower().split()
                    n_parts = n.lower().split()
                    common_parts = set(fn_parts) & set(n_parts)
                    similarity = len(common_parts) / max(len(fn_parts), len(n_parts))
                    if similarity > similarity_limit:
                        #print(f"Skipping vCard with FN: {fn} and N: {n} due to similarity ({similarity:.2f})")
                        break
                    print(f"FN: {fn}, N: {n}, Similarity: {similarity:.2f}")

                if not line.startswith(("FN", "TEL")):
                    continue # do not add

                filtered_lines.append(line)
                    

            #print(f"Filtered lines for vCard: {filtered_lines}, Similarity: {similarity:.2f}")
            if filtered_lines and similarity <= similarity_limit and len(filtered_lines) > 1:
                filtered_vcards.append("BEGIN:VCARD\nVERSION:3.0\n" + "\n".join(filtered_lines) + "\nEND:VCARD")

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(filtered_vcards))

# Example usage
# get current date
yyyymmdd = __import__('datetime').datetime.now().strftime('%Y%m%d')
extract_vcf_info('contacts_v3.vcf', f'contacts_v3_short_{yyyymmdd}.vcf')
