from receipt_parser import parse_receipt

receipt = """
PhonePe

Merchant
Domino's Pizza

UPI Transaction ID
987654321654987

Amount
₹560

02 Jul 2026
"""

result = parse_receipt(receipt)

print(result)