import os

import frappe


def get_ocr_provider():
    settings = frappe.get_single("Rent Pro Settings")
    return getattr(settings, "ocr_provider", "Tesseract") or "Tesseract"


def extract_document(file_url):
    provider = get_ocr_provider()
    if provider == "Google Vision":
        return _extract_google_vision(file_url)
    elif provider == "Azure OCR":
        return _extract_azure(file_url)
    return _extract_tesseract(file_url)


def _extract_tesseract(file_url):
    try:
        import pytesseract
        from PIL import Image

        file_path = _get_file_path(file_url)
        if not file_path:
            return _mock_result("Tesseract")

        img = Image.open(file_path)
        raw_text = pytesseract.image_to_string(img)
        confidence_data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
        confidences = [int(c) for c in confidence_data["conf"] if int(c) > 0]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0

        return {
            "raw_text": raw_text,
            "confidence": round(avg_confidence, 1),
            "provider": "Tesseract",
            **_parse_fields(raw_text),
        }
    except ImportError:
        frappe.log_error(
            title="Rent Pro OCR",
            message="pytesseract not installed. " "Using mock OCR result.",
        )
        return _mock_result("Tesseract")
    except Exception as e:
        frappe.log_error(
            title="Rent Pro OCR Error",
            message=f"Tesseract error: {e}",
        )
        raise


def _extract_google_vision(file_url):
    try:
        from google.cloud import vision

        client = vision.ImageAnnotatorClient()
        file_path = _get_file_path(file_url)
        if not file_path:
            return _mock_result("Google Vision")

        with open(file_path, "rb") as f:
            content = f.read()
        image = vision.Image(content=content)
        response = client.text_detection(image=image)
        texts = response.text_annotations
        raw_text = texts[0].description if texts else ""

        return {
            "raw_text": raw_text,
            "confidence": 85.0,
            "provider": "Google Vision",
            **_parse_fields(raw_text),
        }
    except ImportError:
        frappe.log_error(
            title="Rent Pro OCR",
            message="google-cloud-vision not installed.",
        )
        return _mock_result("Google Vision")
    except Exception as e:
        frappe.log_error(
            title="Rent Pro OCR Error",
            message=f"Google Vision error: {e}",
        )
        raise


def _extract_azure(file_url):
    try:
        from azure.ai.documentintelligence import (
            DocumentIntelligenceClient,
        )

        settings = frappe.get_single("Rent Pro Settings")
        endpoint = getattr(settings, "azure_endpoint", "")
        key = getattr(settings, "azure_key", "")
        if not endpoint or not key:
            return _mock_result("Azure OCR")

        client = DocumentIntelligenceClient(endpoint=endpoint, credential=key)
        file_path = _get_file_path(file_url)
        if not file_path:
            return _mock_result("Azure OCR")

        with open(file_path, "rb") as f:
            poller = client.begin_analyze_document("prebuilt-read", body=f)
        result = poller.result()
        raw_text = result.content if result.content else ""

        return {
            "raw_text": raw_text,
            "confidence": 90.0,
            "provider": "Azure OCR",
            **_parse_fields(raw_text),
        }
    except ImportError:
        frappe.log_error(
            title="Rent Pro OCR",
            message="azure-ai-documentintelligence not installed.",
        )
        return _mock_result("Azure OCR")
    except Exception as e:
        frappe.log_error(
            title="Rent Pro OCR Error",
            message=f"Azure OCR error: {e}",
        )
        raise


def _get_file_path(file_url):
    if file_url.startswith("/files/"):
        site_path = frappe.get_site_path("public", file_url)
        if os.path.exists(site_path):
            return site_path
    if file_url.startswith("/private/files/"):
        site_path = frappe.get_site_path(file_url.lstrip("/"))
        if os.path.exists(site_path):
            return site_path
    return None


def _parse_fields(raw_text):
    import re

    result = {
        "full_name": "",
        "document_number": "",
        "expiry_date": "",
        "date_of_birth": "",
        "license_number": "",
        "country": "",
    }
    if not raw_text:
        return result

    name_patterns = [
        r"(?:Name|Nom|الاسم)[:\s]*(.+)",
        r"(?:Full Name|Nom Complet)[:\s]*(.+)",
    ]
    for pattern in name_patterns:
        match = re.search(pattern, raw_text, re.IGNORECASE)
        if match:
            result["full_name"] = match.group(1).strip()
            break

    doc_patterns = [
        r"(?:N[°o]|Number|Num)[.\s]*(\w{6,})",
        r"(?:CIN| Passport|License)[.\s]*(\w{6,})",
    ]
    for pattern in doc_patterns:
        match = re.search(pattern, raw_text, re.IGNORECASE)
        if match:
            result["document_number"] = match.group(1).strip()
            break

    expiry_patterns = [
        r"(?:Exp|Expiry|Valid|Expiration)[:\s]*" r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
        r"(\d{1,2}[/-]\d{1,2}[/-]\d{4})",
    ]
    for pattern in expiry_patterns:
        match = re.search(pattern, raw_text, re.IGNORECASE)
        if match:
            result["expiry_date"] = match.group(1).strip()
            break

    dob_patterns = [
        r"(?:DOB|Born|Birth|Date de naissance)[:\s]*" r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
    ]
    for pattern in dob_patterns:
        match = re.search(pattern, raw_text, re.IGNORECASE)
        if match:
            result["date_of_birth"] = match.group(1).strip()
            break

    country_patterns = [
        r"(?:Country|Pays|Nationality|Nationalité)[:\s]*(\w+)",
        r"(?:Kingdom of|Republic of)\s+(\w+)",
    ]
    for pattern in country_patterns:
        match = re.search(pattern, raw_text, re.IGNORECASE)
        if match:
            result["country"] = match.group(1).strip()
            break

    return result


def _mock_result(provider):
    return {
        "raw_text": "MOCK OCR RESULT - Provider not available",
        "confidence": 0.0,
        "provider": f"{provider} (mock)",
        "full_name": "",
        "document_number": "",
        "expiry_date": "",
        "date_of_birth": "",
        "license_number": "",
        "country": "",
    }
