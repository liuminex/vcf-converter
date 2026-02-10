import re
import sys

BEGIN_RE = re.compile(r"^BEGIN:VCARD$", re.IGNORECASE)
END_RE = re.compile(r"^END:VCARD$", re.IGNORECASE)
VERSION_RE = re.compile(r"^VERSION:(2\.1|3\.0|4\.0)$", re.IGNORECASE)
PROPERTY_RE = re.compile(r"^[A-Z][A-Z0-9-]*(;[^:]+)?:.+$", re.IGNORECASE)
PARAM_RE = re.compile(r"^[A-Z0-9-]+=[^;:]+$", re.IGNORECASE)

def error(msg, line_no, line, severity="ERROR"):
    print(f"[{severity}] Line {line_no}: {msg}")
    print(f"         >> {line}")

def validate_vcard(lines):
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
                error("Invalid VERSION value", i, line)
            else:
                version = line.split(":", 1)[1]
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
                if "=" not in p and version == "2.1":
                    # vCard 2.1 allows TYPE without =
                    continue
                if "=" in p and not PARAM_RE.match(p):
                    error("Malformed parameter", i, line)

        # Specific rule checks
        prop_name = left.split(";", 1)[0].upper()

        if prop_name == "BDAY" and version == "2.1":
            if ";" in left:
                error("BDAY must not have parameters in vCard 2.1", i, line)

        if prop_name == "ADR":
            fields = value.split(";")
            if len(fields) != 7:
                error("ADR must have exactly 7 components", i, line)

        if prop_name == "TEL" and not ";" in left:
            error("TEL without TYPE (allowed but discouraged)", i, line, severity="WARNING")

        if prop_name == "URL" and version == "2.1":
            error("Multiple URL properties may overwrite in vCard 2.1 clients", i, line, severity="WARNING")

    if in_card:
        error("File ended before END:VCARD", len(lines), "", severity="FATAL")

    if card_count == 0:
        print("[FATAL] No vCard found")

    print(f"\nValidation finished. Cards found: {card_count}")

def main():
    with open("contacts_v2.vcf", encoding="utf-8") as f:
        lines = f.readlines()

    validate_vcard(lines)

if __name__ == "__main__":
    main()
