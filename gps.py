import requests
#from app import app
import pandas as pd
def get_lat_lon(file_path):
    def to_decimal(coord, ref):
        deg = coord[0][0] / coord[0][1]
        min_ = coord[1][0] / coord[1][1]
        sec = coord[2][0] / coord[2][1]
        dec = deg + min_/60 + sec/3600
        if ref in ['S', 'W']:
            dec = -dec
        return dec

    with open(file_path, 'rb') as f:
        data = f.read()

    start = data.find(b'Exif\x00\x00')
    if start == -1:

        return None

    exif = data[start+6:]
    endian = 'little' if exif[:2] == b'II' else 'big'

    def read_short(offset):
        return int.from_bytes(exif[offset:offset+2], endian)
    def read_long(offset):
        return int.from_bytes(exif[offset:offset+4], endian)

    ifd_offset = read_long(4)
    num_entries = read_short(ifd_offset)
    
    gps_offset = None
    for i in range(num_entries):
        entry = ifd_offset + 2 + i*12
        if read_short(entry) == 0x8825: 
            gps_offset = read_long(entry + 8)
            break
    if gps_offset is None:
        return None

    num_gps_entries = read_short(gps_offset)
    gps = {}
    for i in range(num_gps_entries):
        entry = gps_offset + 2 + i*12
        tag = read_short(entry)
        value_offset = read_long(entry + 8)

        if tag == 1:  
            gps['lat_ref'] = exif[value_offset:value_offset+2].decode(errors='ignore').strip('\x00')
        elif tag == 2:  
            gps['lat'] = [(read_long(value_offset+j*8), read_long(value_offset+j*8+4)) for j in range(3)]
        elif tag == 3: 
            gps['lon_ref'] = exif[value_offset:value_offset+2].decode(errors='ignore').strip('\x00')
        elif tag == 4:  
            gps['lon'] = [(read_long(value_offset+j*8), read_long(value_offset+j*8+4)) for j in range(3)]

    if 'lat' in gps and 'lon' in gps:
        return to_decimal(gps['lat'], gps['lat_ref']), to_decimal(gps['lon'], gps['lon_ref'])
    return None


def reverse_geocode(lat, lon):
    url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
    headers = {"User-Agent": "geo-app"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data.get("display_name")
    else:
        return None


coords = get_lat_lon('IMG_5700.jpg')
if coords:
    print("Latitude:", coords[0], "Longitude:", coords[1])
    address = reverse_geocode(*coords)

    if address:
        print("Address:", address)
    else:
        print("GPS found, but no address returned.")
else:
    print("No GPS info found in this photo.")
data = {
    'City': ["West Bengal", "Kochi", "Chennai", "Mumbai", "Goa", "Sundarbans"],
    'Pincode': ['700001', '682001', '600001', '400001', '403001', '743370'],
    'Forest': ['Sundarbans', 'Vypin Island Mangroves', 'Pulicat Lake Mangroves', 'Thane Creek Mangroves', 'Mandovi and Zuari Estuary Mangroves', 'Sundarbans Mangrove Forest'],
    'Latitude': [22.5726, 9.9312, 13.0827, 19.0760, 15.2993, 21.9333],
    'Longitude': [88.3639, 76.2673, 80.2707, 72.8777, 74.1240, 88.8500],
}
df = pd.DataFrame(data)
def check_mangrove(address, df):
    add = [x.strip() for x in address.split(",")] 
    for i in add:
        if i in df['City'].values:
            forest = df[df['City'] == i]['Forest'].values[0]
            return i, f"Mangrove forest found: {forest} in City: {i}"
        elif i in df['Pincode'].values:
            forest = df[df['Pincode'] == i]['Forest'].values[0]
            return f"Mangrove forest found: {forest} in Pincode: {i}"
    return None, "No mangrove forest recorded nearby."

print(check_mangrove(address,df))

