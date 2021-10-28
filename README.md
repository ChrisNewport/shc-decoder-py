# Smart Health Card Decoder

Decode QR Codes conforming to the Smart Health Card (SHC) [specification](https://spec.smarthealth.cards/)

---

## DISCLAIMER !
**FOR EDUCATIONAL PURPOSES ONLY WITH ABSOLUTELY NO WARRANTY OF ANY KIND!**  
- Developer takes no responsibility for illegal or unauthorized use by any third party.  
- No affiliation with any government  
- *CANNOT* be used for verifying proof of vaccination in *any way*.  
- **Use only authorized official applications for your jurisdiction.**  
- Decodes and checks for a valid signature, however it *DOES NOT* check/validate/verify any information in the payload **AT ALL**!  
- Not to be used to collect personal data without express consent of the data owner.  

---

## Information

Currently supports decoding of most Canadian issued QR codes.  
Additional provinces and territories will be added when available.

Currently **not** supported:
- Manitoba
- New Brunswick
- Nunavut
- PEI

---

## Installation / Usage
Creating a virtual environment with `venv` is recommended.  
Download or clone git repo then install required packages.  
`pip` and `setuptools` should also be updated or `cryptography` may fail to install.
```
python -m pip install --upgrade pip
python -m pip install --upgrade setuptools
pip install -r requirements.txt
```

Decode a local PNG image of QR code
```
python shc_decode.py -i qr_code.png
```

Live decoding via web camera
```
python shc_decode.py
```

## Known issues
In Windows, USB web cameras can sometimes take a *looong time* to fully initialize in OpenCV.  
A possible [workaround](https://github.com/opencv/opencv/issues/17687) involves setting an environment variable.
```
OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS=0
```

---

### Credit / Inspiration
 * https://github.com/obrassard/shc-extractor
 * https://github.com/dvci/health-cards-walkthrough/blob/main/SMART%20Health%20Cards.ipynb
 * https://www.pyimagesearch.com/2018/05/21/an-opencv-barcode-and-qr-code-scanner-with-zbar/