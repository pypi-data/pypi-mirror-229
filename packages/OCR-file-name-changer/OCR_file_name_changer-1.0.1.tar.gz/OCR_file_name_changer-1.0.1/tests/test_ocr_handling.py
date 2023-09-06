import unittest

from ocr_file_name_changer.ocr_handling import *
from samples import *


class TestOCRHandling(unittest.TestCase):

    def test_extract_sn_from_image_invalid_samples(self):
        for img_path in INVALID_SAMPLE_PATHS:
            with self.assertRaises(IncorrectImageException, msg=f"Sample {img_path} seems valid"):
                extract_sn_from_img(img_path)

    def test_extract_sn_from_image_valid_samples(self):
        for img_path, expected_sn in VALID_SAMPLES.items():
            sn = extract_sn_from_img(img_path)
            msg = f"Wrong sn in sample: f{img_path}: \nexpected: {expected_sn}\nactual:   {sn}"
            self.assertTrue(expected_sn in sn, msg=msg)
