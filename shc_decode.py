'''
Smart Health Card Decoder

DISCLAIMER: FOR EDUCATIONAL PURPOSES ONLY WITH ABSOLUTELY NO WARRANTY OF ANY KIND!
Developer disclaims any responsibility for illegal use by any third party.
No affiliation with any government
Decodes and checks for a valid signature, however it *DOES NOT* check any information in the payload AT ALL!
Not to be used to collect personal data without express consent of the data owner.
CANNOT be used for verifying proof of vaccination in any way.
Use only authorized official applications for your jurisdiction.


Usage:
-i or --image to decode a PNG image containing an SHC QR code.
With no arguments, script will attempt to use a connected camera for live decoding
'''
from imutils.video import VideoStream
from pyzbar import pyzbar
import jwt, json, zlib
import argparse
import imutils, cv2
import time

# JSON Web Key Sets
# Some issuers have multiple key identifiers for the same key.
# Saskatchewan actually has two different keys.
# This is fine since we blindly test all keys to validate a signature.
nl_jwks = '{"keys":[{"kty":"EC","kid":"UboztS3pE1mr0dnG7Rv24kRNqlYbHrbxd-qBFerpZvI","use":"sig","alg":"ES256","crv":"P-256","x":"mB0PKTVRnr3JCtyucEjCHXkXW3COg5KP0y4gKCNJxWc","y":"PTpxiYECNiuyRwpwqjme8OIFdG7N-HwN2XH02phdZCs","date":1632779181394}]}'
ns_jwks = '{"keys":[{"kty":"EC","kid":"UJrT9jU8vOCUl4xsI1RZjOPP8hFUv7n9mhVtolqH9qw","use":"sig","alg":"ES256","crv":"P-256","x":"kIaIeOhhxpiN13sDs6RKVzCpvxxObI9adKF5YEmKngM","y":"AZPQ7CHd3UHp0i4a4ua1FhIq8SJ__BuHgDESuK3A_zQ"}]}'
#nb_jwks = ''
#pe_jwks = ''
qc_jwks = '{"keys":[{"kty":"EC","kid":"2XlWk1UQMqavMtLt-aX35q_q9snFtGgdjH4-Y1gfH1M","use":"sig","alg":"ES256","crv":"P-256","x":"XSxuwW_VI_s6lAw6LAlL8N7REGzQd_zXeIVDHP_j_Do","y":"88-aI4WAEl4YmUpew40a9vq_w5OcFvsuaKMxJRLRLL0"}]}'
on_jwks = '{"keys":[{"kty":"EC","kid":"Nlgwb6GUrU_f0agdYKc77sXM9U8en1gBu94plufPUj8","use":"sig","alg":"ES256","crv":"P-256","x":"ibapbMkHMlkR3D-AU0VTFDsiidQ49oD9Ha7VY8Gao3s","y":"arXU5frZGOvTZpvg045rHC7y0fqVOS3dKqJbUYhW5gw"}]}'
#mb_jwks = ''
sk1_jwks = '{"keys":[{"kty":"EC","use":"sig","crv":"P-256","kid":"xOqUO82bEz8APn_5wohZZvSK4Ui6pqWdSAv5BEhkes0","x":"Hk4ktlNfoIIo7jp5I8cefp54Ils3TsKvKXw_E9CGIPE","y":"7hVieFGuHJeaNRCxVgKeVpoxDJevytgoCxqVZ6cfcdk","alg":"ES256"}]}'
sk2_jwks = '{"keys":[{"alg":"ES256","crv":"P-256","kid":"RBvL32MBD4FXqXKE86HU9Nnjp0hADhqztOXb-M_mP_k","kty":"EC","use":"sig","x":"p9Rf7Wh1_vCMTK4i4XLQFI6_LR0ZhISQVJ2PAy2yEdA","y":"ai71citYuk72ldpGiwRZ0NfZGJPzKZBVulaUv_74IjY"}]}'
ab_jwks = '{"keys":[{"kty":"EC","kid":"JoO-sJHpheZboXdsUK4NtfulfvpiN1GlTdNnXN3XAnM","use":"sig","alg":"ES256","crv":"P-256","x":"GsriV0gunQpl2X9KgrDZ4EDCtIdfOmdzhdlosWrMqKk","y":"S99mZMCcJRsn662RaAmk_elvGiUs8IvSA7qBh04kaw0"}]}'
bc_jwks = '{"keys":[{"kty":"EC","kid":"XCqxdhhS7SWlPqihaUXovM_FjU65WeoBFGc_ppent0Q","use":"sig","alg":"ES256","crv":"P-256","x":"xscSbZemoTx1qFzFo-j9VSnvAXdv9K-3DchzJvNnwrY","y":"jA5uS5bz8R2nxf_TU-0ZmXq6CKWZhAG1Y4icAx8a9CA"}]}'
yt_jwks = '{"keys":[{"kty":"EC","kid":"UnHGY-iyCIr__dzyqcxUiApMwU9lfeXnzT2i5Eo7TvE","use":"sig","alg":"ES256","crv":"P-256","x":"wCeT9rdLYTpOK52OK0-oRbwDxbljJdNiDuxPsPt_1go","y":"IgFPi1OrHtJWJGwPMvlueeHmULUKEpScgpQtoHNjX-Q"}]}'
nt_jwks = '{"keys":[{"kty":"EC","kid":"8C-9TNgyGuOqc-3FXyNRq6m5U9S1wyhCS1TvpgjzkoU","use":"sig","alg":"ES256","crv":"P-256","x":"C-9Lltax_iU6iYdK8DdCZzv4cQN6SFVUG7ACaCT_MKM","y":"_qaENBMJz6iLf1qyYMx2_D6fXxbbNoHbLcfdPF9rUI0","date":1631112755371}]}'
#nu_jwks = ''

jwks_list = {
    'Newfoundland & Labrador': nl_jwks,
    'Nova Scotia': ns_jwks,
    'Quebec': qc_jwks,
    'Ontario': on_jwks,
    'Saskatchewan (Key 1)': sk1_jwks,
    'Saskatchewan (Key 2)': sk2_jwks,
    'Alberta': ab_jwks,
    'British Columbia': bc_jwks,
    'Yukon': yt_jwks,
    'Northwest Territories': nt_jwks
    }


def shc_qr_to_token(data):
    ''' decode SHC numeric format to base64url encoded JWT'''
    char = ""
    print("length:",len(data))
    for x in range(0,len(data),2):
        char += (chr(int(data[x] + data[x+1]) + 45))
    print("decoded: ",char)
    return (char.split('.'))

def parse_shc_token(data):
    ''' parse SHC JWT into header, payload, and signature '''
    for qrcode in data:
        qrcodeData = qrcode.data.decode("utf-8")
        qrcodeType = qrcode.type
        if(qrcodeType == "QRCODE"):
            print(f"[INFO] Found QRCODE: {qrcodeData}")
            if(qrcodeData[:5].lower() == "shc:/"):
                print("Smart Health Card Format Detected!")
                shc_data = qrcodeData.split('/')[1]
                return shc_qr_to_token(shc_data)
    print("No Smart Health Card QR Codes Found!")

def print_and_verify_shc_token(header, payload, sig):
    hdrdecoded = jwt.utils.base64url_decode(header)
    print("\n\n\n")
    print("header: ",hdrdecoded.decode())
    payloaddecoded = jwt.utils.base64url_decode(payload)
    # payload is compressed with DEFLATE as per SHC spec
    payload_decompressed = zlib.decompress(payloaddecoded,-8)
    
    json_object = json.loads(payload_decompressed)
    print("payload: ")
    print(json.dumps(json_object, indent=3))
    
    jwt_encoded = header + "." + payload + "." + sig
    for issuer, jwks in jwks_list.items():
        for key_dict in json.loads(jwks)['keys']:
            pub_key = jwt.algorithms.ECAlgorithm.from_jwk(json.dumps(key_dict))
        try:
            # PyJWT needs modification to support DEFLATE with jwt.decode,
            # must use jwt.api_jws.decode just for signature verification
            # (payload manually decompressed above)
            #jwt.decode(jwt_encoded,pub_key,algorithms=["ES256"])
            jwt.api_jws.decode(jwt_encoded,pub_key,algorithms=["ES256"])
            print(f"valid sig from {issuer}")
        except jwt.exceptions.InvalidSignatureError:
            #print("invalid sig")
            pass


ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", type=str, help="path to PNG of QR code")
args = vars(ap.parse_args())

if(args["image"]):
    # load the input image
    image = cv2.imread(args["image"])
    # find the barcodes in the image and decode each of the barcodes
    qrcodes = pyzbar.decode(image)
    header, payload, sig = parse_shc_token(qrcodes)
    print_and_verify_shc_token(header, payload, sig)
    exit()

print("[INFO] no input image provided.. starting video capture...")
# initialize the video stream and allow the camera sensor to warm up
# In Windows, may be helpful to set this environment variable for faster camera initialization
# OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS=0
vs = VideoStream(src=0).start()
#vs = VideoStream(usePiCamera=True).start()
time.sleep(2.0)
found = set()

while True:
    # grab the frame from the threaded video stream and resize it to
    # have a maximum width of 900 pixels
    frame = vs.read()
    frame = imutils.resize(frame, width=900)
    qrcodes = pyzbar.decode(frame)
    # loop over the detected qrcodes
    for qrcode in qrcodes:
        qrcodeData = qrcode.data.decode("utf-8")
        if(qrcodeData[:5].lower() == "shc:/"):
            (x, y, w, h) = qrcode.rect
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
            text = "Smart Health Card Found!"
            cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            if qrcodeData not in found:
                header, payload, sig = parse_shc_token(qrcodes)
                print_and_verify_shc_token(header, payload, sig)
                found.add(qrcodeData)
    cv2.imshow("QR Smart Health Card Scanner", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break

print("[INFO] cleaning up...")
cv2.destroyAllWindows()
vs.stop()

