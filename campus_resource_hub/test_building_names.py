"""Quick test of building name extraction"""

def extract_building_name(address):
    """Extract and normalize building name from full address"""
    if not address:
        return None
    if ',' in address:
        building = address.split(',')[0].strip()
    else:
        import re
        match = re.match(r'^([^\d]+)', address)
        building = match.group(1).strip() if match else address.strip()
    
    # Normalize common building name variations
    if 'herman b wells library' in building.lower() or building.lower() == 'wells library':
        return 'Wells Library'
    elif 'kelley school of business' in building.lower():
        return 'Kelley School of Business'
    elif 'indiana memorial union' in building.lower() or building.lower() == 'imu':
        return 'Indiana Memorial Union (IMU)'
    elif 'luddy hall' in building.lower():
        return 'Luddy Hall'
    elif 'wright education' in building.lower():
        return 'Wright Education Building'
    elif 'jacobs school of music' in building.lower():
        return 'Jacobs School of Music'
    elif 'multidisciplinary science building' in building.lower() or 'msb' in building.lower():
        return 'Multidisciplinary Science Building II'
    elif 'chemistry building' in building.lower():
        return 'Chemistry Building'
    elif 'student center' in building.lower():
        return 'Student Center'
    elif 'student recreational sports center' in building.lower() or 'srsc' in building.lower():
        return 'Student Recreational Sports Center'
    else:
        return building

# Test cases
test_addresses = [
    "Herman B Wells Library, Level 2, 1320 E 10th St",
    "Wells Library, Checkout Desk, Level 1",
    "Kelley School of Business (Hodge Hall), 2nd Floor, 1309 E 10th St",
    "Luddy Hall, Room 150, 700 N Woodlawn Ave",
    "Indiana Memorial Union, 2nd Floor, 900 E 7th St"
]

print("Testing building name extraction:")
for addr in test_addresses:
    result = extract_building_name(addr)
    print(f"  {addr[:50]}... => {result}")
