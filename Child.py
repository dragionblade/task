import os
import re
from Utility import Utility

class Child(Utility):

    def getMasterDataFilePath(self):
        # Uses absolute path to ensure the file is found regardless of where the script is run
        return os.path.abspath(os.path.join(os.path.dirname(__file__), "master_data.csv"))

    def extractAmountAndCurrency(self, message):
        currency_map = {
            'rs': 'INR', 'rs.': 'INR', '₹': 'INR', 'rupees': 'INR', 
            'inr': 'INR', 'inr.': 'INR',
        }

        if not message:
            return ["", ""]

        text = message.lower()
        
        # Sort keys by length descending to match 'rs.' before 'rs'
        currency_pattern = r'|'.join(re.escape(t) for t in sorted(currency_map.keys(), key=len, reverse=True))
        
        multiplier_map = {
            'lac': 100000, 'lacs': 100000, 'lakh': 100000, 'lakhs': 100000,
            'k': 1000, 'thousand': 1000, 'thousands': 1000,
            'crore': 10000000, 'crores': 10000000, 'cr': 10000000
        }
        multiplier_pattern = r'|'.join(re.escape(t) for t in sorted(multiplier_map.keys(), key=len, reverse=True))

        # Improved Pattern: Matches (Currency)(Amount)(Multiplier) or (Amount)(Multiplier)(Currency)
        # Handles commas and decimals
        amt_regex = rf'[\d,]+(?:\.\d+)?(?:\s*(?:{multiplier_pattern}))?'
        patterns = [
            rf'(?P<curr>{currency_pattern})\s*(?P<amt>{amt_regex})',
            rf'(?P<amt>{amt_regex})\s*(?P<curr>{currency_pattern})',
        ]

        scored_matches = []
        
        for pattern in patterns:
            for m in re.finditer(pattern, text):
                curr_token = m.group('curr').strip()
                amt_raw = m.group('amt').strip()
                
                # Check for '+' immediately following the match (e.g., "1000+")
                if m.end() < len(text) and text[m.end()] == '+':
                    continue

                # Parse the numeric value
                try:
                    # Isolate the numeric part from the multiplier
                    num_match = re.search(r'[\d,]+(?:\.\d+)?', amt_raw)
                    if not num_match: continue
                    
                    val = float(num_match.group().replace(',', ''))
                    
                    # Apply multiplier
                    for mult_key, factor in multiplier_map.items():
                        if mult_key in amt_raw:
                            val *= factor
                            break
                    
                    # Store tuple: (numeric_value, start_index, end_index, currency_token)
                    scored_matches.append({
                        'val': val,
                        'start': m.start(),
                        'curr': curr_token
                    })
                except ValueError:
                    continue

        if not scored_matches:
            return ["", ""]

        # Sort matches by their appearance in the text
        scored_matches.sort(key=lambda x: x['start'])

        # --- BUSINESS LOGIC HEURISTICS ---
        # 1. If 'recharge' is present, prioritize the amount closest to the word 'recharge'
        if "recharge" in text:
            recharge_pos = text.find("recharge")
            target = min(scored_matches, key=lambda x: abs(x['start'] - recharge_pos))
        
        # 2. If 'credit limit' or 'upto' is present (Flipkart/Airtel cases), 
        # the Expected Amount is often the smaller 'Gift Card' or 'Processing fee' value.
        elif any(k in text for k in ["limit", "upto", "up to", "win"]):
            # Usually the smaller amount is the actual target (e.g., 500 off vs 5lac loan)
            target = min(scored_matches, key=lambda x: x['val'])
        
        # 3. Default: Take the first valid currency-amount pair found
        else:
            target = scored_matches[0]

        # Final Formatting
        amount_formatted = f"{target['val']:.2f}"
        currency = currency_map.get(target['curr'].lower(), target['curr'].upper())

        return [amount_formatted, currency]