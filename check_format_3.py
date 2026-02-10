import re
import sys

BEGIN_RE = re.compile(r"^BEGIN:VCARD$", re.IGNORECASE)
END_RE = re.compile(r"^END:VCARD$", re.IGNORECASE)
VERSION_RE = re.compile(r"^VERSION:3\.0$", re.IGNORECASE)
PROPERTY_RE = re.compile(r"^[A-Z][A-Z0-9-]*(;[^:]+)?:.+$", re.IGNORECASE)
PARAM_RE = re.compile(r"^[A-Z0-9-]+=[^;:]+$", re.IGNORECASE)

def error(msg, line_no, line, severity="ERROR"):
    print(f"[{severity}] Line {line_no}: {msg}")
    print(f"         >> {line}")

def validate_vcard_v3(lines):
    in_card = False
    version = None
    card_count = 0

    for i, raw in enumerate(lines, start=1):
        line = raw.rstrip("\n")

        if not line:
            continue

        if BEGIN_RE.match(line):
            if in_card:
                error("Nested BEGIN:VCARD", i, line)
            in_card = True
            version = None
            card_count += 1
            continue

        if END_RE.match(line):
            if not in_card:
                error("END:VCARD without BEGIN:VCARD", i, line)
            in_card = False
            version = None
            continue

        if not in_card:
            error("Line outside of vCard block", i, line)
            continue

        # VERSION
        if line.upper().startswith("VERSION:"):
            if not VERSION_RE.match(line):
                error("VERSION must be 3.0", i, line)
            else:
                version = "3.0"
            continue

        # Property format check
        if not PROPERTY_RE.match(line):
            error("Invalid property syntax", i, line)
            continue

        # Split name/params from value
        left, value = line.split(":", 1)

        # Check parameters
        if ";" in left:
            parts = left.split(";")
            prop = parts[0]
            params = parts[1:]

            for p in params:
                if "=" not in p:
                    error(f"Parameter missing '=' in vCard 3.0 (TYPE must be like TYPE=value)", i, line)
                elif not PARAM_RE.match(p):
                    error("Malformed parameter", i, line)

        # Specific v3 checks
        prop_name = left.split(";", 1)[0].upper()

        if prop_name == "BDAY":
            if ";" in left:
                error("BDAY must not have parameters in vCard 3.0", i, line)
            if not re.match(r"^\d{8}$", value):
                error("BDAY must be in YYYYMMDD format", i, line)

        if prop_name == "ADR":
            fields = value.split(";")
            if len(fields) != 7:
                error("ADR must have exactly 7 components", i, line)

        if prop_name == "TEL":
            if not any(p.upper().startswith("TYPE=") for p in left.split(";")[1:]):
                error("TEL missing TYPE parameter in vCard 3.0", i, line, severity="WARNING")

    if in_card:
        error("File ended before END:VCARD", len(lines), "", severity="FATAL")

    if card_count == 0:
        print("[FATAL] No vCard found")

    print(f"\nValidation finished. vCard 3.0 cards found: {card_count}")

def main():

    with open("contacts_v3.vcf", encoding="utf-8") as f:
        lines = f.readlines()

    validate_vcard_v3(lines)

if __name__ == "__main__":
    main()
