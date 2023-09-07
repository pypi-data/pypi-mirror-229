from paddleocr import PaddleOCR

from .exceptions import IncorrectImageException

ocr = PaddleOCR(use_angle_cls=True, lang='pl', show_log=False)


def extract_sn_from_img(img_path: str) -> str:
    result = ocr.ocr(img_path, cls=True)
    extracted_strings = _get_result_strings(result)

    if len(extracted_strings) > 1:
        msg = f"Z pliku {img_path} odczytano wiecej niz 1 napis"
        raise IncorrectImageException(msg)

    final_string = "".join(extracted_strings)
    final_string = _remove_colon(final_string)
    return final_string


def _get_result_strings(result) -> list[str]:
    return [line[1][0] for line in result[0]]


def _remove_colon(final_string: str) -> str:
    return final_string.replace(":", " ")
