import re

def v4_to_v2(v4_file, v2_file):
    with open(v4_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    v2_lines = []
    photo_data = ""
    in_photo = False

    notes = []

    for line in lines:

        if line.startswith("PRODID") or line.startswith(" ") or line.startswith("PHOTO"):
            # skip
            continue

        if line.startswith("END:VCARD"):

            # merge notes and add line:
            if notes:
                v2_lines.append("NOTE:" + "\\n".join(notes))
                notes = []

            v2_lines.append(line)
            continue

        # replace PREF=1 with none
        line = line.replace(";PREF=1", "")
        line = line.replace(";PREF=2", "")
        line = line.replace(";PREF=3", "")
        line = line.replace(";PREF=4", "")
        line = line.replace(";PREF=5", "")
        line = line.replace(";PREF=undefined", "")

        if line.startswith("NOTE:"):
            # collect notes to merge later
            note = line.split("NOTE:",1)[1].strip()
            notes.append(note)
            continue

        if line.startswith("URL"):
            continue # skip for now




            # add to notes:
            url = line.split(":",1)[1].strip()
            notes.append("URL: " + url)
            continue

        # Convert version
        if line.startswith("VERSION:4.0"):
            v2_lines.append("VERSION:2.1")
            continue

        # Convert FN/N lines (remove v4 attributes)
        if line.startswith("FN:"):
            parts = line.split(":")
            if len(parts) > 2:
                raise ValueError(f"Unexpected FN format: {line}")
            name = parts[1].strip()
            name = name.replace(" ", ";")

            # invert position of first and last name
            parts = name.split(";")
            
            # invert array:
            parts = parts[::-1]
            name = ";".join(parts)

            # add missing ; to have total 4:
            missing_sc = 4 - name.count(";")
            v2_lines.append("N:" + name + ";"*missing_sc)
            continue
        if line.startswith("N:"):
            parts = line.split(":")
            if len(parts) > 2:
                raise ValueError(f"Unexpected N format: {line}")
            
            name = parts[1].strip()
            name = name.replace(";", " ")

            # also add as note
            notes.append("N: " + name)

            v2_lines.append("FN:" + name) # add n as fn
            continue

    

        # ADR;HOME:;;Greece, Athens;;;;
        if line.upper().startswith("ADR"):
            # Extract value after ":"
            parts = line.split(":", 1)
            if len(parts) < 2:
                value = ""
            else:
                value = parts[1].strip()

            # Remove v4-specific inline parameters like PREF=1 or TYPE=x-addr
            value = re.sub(r"(PREF=\d+|TYPE=[^;:]*)", "", value, flags=re.IGNORECASE)

            # Split by semicolons to preserve existing ADR structure
            comps = value.split(";")

            # Strip extra spaces/dashes from each component
            comps = [c.strip("- ").strip() for c in comps]

            


            # Pad or truncate to exactly 7 components
            while len(comps) < 7:
                comps.append("")
            comps = comps[:7]

            if not comps[2]: comps[2] = "-"
            if not comps[3]: comps[3] = "-"

            # Build v2.1 ADR line
            v2_lines.append("ADR:" + ";".join(comps))
            continue




        if line.startswith("TEL"):
            # Remove v4 attributes but keep essential type
            parts = line.replace(";PREF=1", "").split(":",1)
            tel = parts[1].strip()
            v2_lines.append("TEL;VOICE;CELL:" + tel)
            continue

        if line.startswith("BDAY"):
            # convert to yyyy-mm-dd format
            bday = line.split(":",1)[1].strip()
            if re.match(r'^\d{8}$', bday):
                bday = f"{bday[0:4]}-{bday[4:6]}-{bday[6:8]}"
            v2_lines.append("BDAY:" + bday)
            continue

        if line.startswith("ITEM") and "EMAIL" in line:
            # Remove v4 attributes but keep email
            parts = line.replace(";PREF=1", "").split(":",1)
            email = parts[1].strip()
            v2_lines.append("EMAIL:" + email)
            continue

    
                           


        # else add the line as is:
        v2_lines.append(line)


    # in all lines remove \n and \r
    v2_lines = [line.replace("\n", "").replace("\r", "") for line in v2_lines]

    # Write v2 output
    with open(v2_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(v2_lines))
    print(f"Converted {v4_file} to {v2_file}")

# Example usage
v4_to_v2("contacts_v4.vcf", "contacts_v2.vcf")
