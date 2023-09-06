import re
import traceback
import json
import decimal
from .parse_classification_page_range import parse_page_range


def get_main_schema():
    main_schema = {
        "headers": {
            "Classify Document": {
                "classification": "N/A"
            }
        },
        "tables": {
            "Document Classifications": [
                {
                    "Page Rows": [
                        {"doc_type": "N/A", "page_nums": "0"},
                        {"doc_type": "N/A", "page_nums": "0"}
                    ]
                }
            ]
        }
    }
    return main_schema


DT_CLASSIFICATION_MAP = {
    "rate_confirmation": "Rate Confirmation (ratecon)",
    "bill_of_lading": "Bill of Lading (BOL)",
    "noa_lor": "Notice of Assignment (NOA)",
    "noa": "Notice of Assignment (NOA)",
    "lor": "Letter of Rescission (LOR)",
    "scale_ticket": "Scale Ticket",
    "packing_list": "Packing List",
    "drayage": "Drayage",
    "chassis": "Chassis",
    "detention": "Detention",
    "lumper": "Lumper",
    "other": "OTHER",
    "receipt": "Receipt",
    "invoice": "Invoice",
    None: "N/A"
}


def dt_multiclass_to_dynamoson(autoextracts_data, page_length):
    """
    Reformats the DTs multiclass data format into the mutually agreed upon Dynamoson structure;
    :param autoextracts_data: dict,;
    :param page_length: int,;
    :return:
    """
    func = dt_multiclass_to_dynamoson.__name__
    base_schema = {
        "headers": {
            "Classify Document": {
                "classification": "MULTIPLE"
            }
        },
        "tables": {
            "Document Classifications": [
                {
                    "Page Rows": []
                }
            ]
        }
    }
    try:
        for num, class_dict in autoextracts_data.items():
            pages = [str(i) for i in class_dict['singles']]
            page_nums = ", ".join(pages)
            doc_class = class_dict['classification']
            try:
                doc_class = DT_CLASSIFICATION_MAP[doc_class]
            except Exception as ee:
                print(f"[WARN] {doc_class} not found in DT_CLASSIFICATION_MAP ==> {ee}")

            row = {
                'doc_type': doc_class,
                'page_nums': page_nums
            }
            base_schema['tables']['Document Classifications'][0]['Page Rows'].append(row)
        try:
            sorted_results = sorted(base_schema['tables']['Document Classifications'][0]['Page Rows'], key=lambda k: max([int(i) for i in k['page_nums']]))
            print(f"[DEBUG] sorted preclassifications: {sorted_results}")
            base_schema['tables']['Document Classifications'][0]['Page Rows'] = sorted_results
        except Exception as se:
            print(f"[WARN] Sort Error ==> {se}")
            traceback.print_exc()

        if len(base_schema['tables']['Document Classifications'][0]['Page Rows']) == 0:
            for i in list(range(0, page_length)):
                base_schema['tables']['Document Classifications'][0]['Page Rows'].append(
                    {
                        "doc_class": "N/A",
                        "page_nums": str(i + 1)
                    }
                )

        return True, base_schema, ""

    except Exception as e:
        print(f"[ERROR] {func} Error ==> {e}")
        traceback.print_exc()
        return False, base_schema, f"{e}"


def classification_template(doc, multi_class=False):
    func = classification_template.__name__
    try:
        assert isinstance(doc, dict), f"Expected dictionary DataType for document, but got <{type(doc)}> instead."

        if multi_class:
            print(f"[PARSING PRE-CLASSIFIED PAGES] {doc['autoextracts']['data']}")
            success, dynamoson, err = dt_multiclass_to_dynamoson(
                autoextracts_data=doc["autoextracts"]["data"],
                page_length=len(doc['image_filenames'])
            )
            if not success:
                raise Exception(f"dt_multiclass_to_dynamoson() encountered an error ==> {err}")
            ddb_copy = doc.copy()
            ddb_copy["autoextracts"]["data"] = dynamoson
            return True, ddb_copy, ""

        else:
            ddb_copy = doc.copy()
            ddb_copy["autoextracts"]["data"] = get_main_schema()
            return True, ddb_copy, ""

    except Exception as e:
        print(f"[ERROR] {func} Error ==> {e}")
        traceback.print_exc()
        return False, None, f"{e}"


def standardize_classification_name(classification: str):
    """
    Takes in a string classification choice from the DT and parses it into a standard format.
    """
    func = standardize_classification_name.__name__
    try:
        class_names = [
            "rate_confirmation", "bill_of_lading", "noa_lor", "packing_list", "scale_ticket", "invoice", "receipt",
            "chassis", "detention", "drayage", "other", "multiple", "lumper"
        ]

        if classification.lower() in ["ratecon", "rate con", "rate confirmation", "rate_confirmation", "rate confirmation (ratecon)"]:
            classification = "rate_confirmation"
        elif "ratecon" in classification.lower() or "rate con" in classification.lower():
            classification = "rate_confirmation"
        elif classification.lower() in ["bol", "bill of lading", "bill_of_lading", "bill of lading (bol)"]:
            classification = "bill_of_lading"
        elif "bill of lading" in classification.lower() or "bol" in classification.lower():
            classification = "bill_of_lading"
        elif classification.lower() in ["noa", "lor", "noa-lor", "noalor", "noa_lor"]:
            classification = "noa_lor"
        elif "noa" in classification.lower() or "lor" in classification.lower():
            classification = "noa_lor"
        elif classification.lower() in ["packing list", "packing-list", "packing_list"]:
            classification = "packing_list"
        elif classification.lower() == "invoice":
            classification = classification.lower()
        elif classification.lower() == "lumper":
            classification = classification.lower()
        elif classification.lower() == "receipt":
            classification = classification.lower()
        elif classification.lower() in ["scale ticket", "scale_ticket", "scale-ticket"]:
            classification = "scale_ticket"
        elif classification.lower() == "drayage":
            classification = classification.lower()
        elif classification.lower() in ["chassis", "chaissis"]:
            classification = "chassis"
        elif classification.lower() == "detention":
            classification = classification.lower()
        elif classification.lower() in ["other", "na", "n/a"]:
            classification = "other"
        elif classification.lower() == "multiple":
            classification = classification.lower()

        if classification not in class_names:
            raise Exception(f"[WARN] {classification} not accounted for!")

        return True, classification, ""

    except Exception as e:
        print(f"[ERROR] {func} Error ==> {e}")
        traceback.print_exc()
        return False, None, f"{e}"


def parse_classification_dynamoson(flattened_ddb_entry: str) -> tuple[bool, str, str]:
    func = parse_classification_dynamoson.__name__
    try:
        if isinstance(flattened_ddb_entry, dict):
            flattened_ddb_entry = json.dumps(flattened_ddb_entry)
        data = json.loads(flattened_ddb_entry, parse_float=decimal.Decimal)
        print(f"[{func}] dynamoson: {data}")
        classification_ = data['headers']['Classify Document']['classification']
        stand_success, classification, stand_err = standardize_classification_name(classification_)
        if not stand_success:
            raise Exception(f"standardize_classification_name() >>> {stand_err}")
        print(f"[{func}] returning {classification}")
        return True, classification, ""
    except Exception as e:
        print(f"[ERROR] {func} Error ==> {e}")
        traceback.print_exc()
        return False, "None", f"{e}"


def parse_multiple_classification_dynamoson(dynamoson: str, ddb_doc_entry, req_id) -> tuple[bool, dict, str]:
    """
    When the ['headers']['Classify Document']['classification'] of the Dynamoson == "MULTIPLE",
    Re-parse the dynamoson to look at the ['tables']['Document Classifications'] (array of objects)
    to get the doc-by-doc classification for this concatenated image.
    """
    func = parse_multiple_classification_dynamoson.__name__
    classification_dict = {}
    try:
        if isinstance(dynamoson, dict):
            dynamoson = json.dumps(dynamoson)

        if isinstance(ddb_doc_entry, str):
            ddb_doc_entry = json.loads(ddb_doc_entry)

        image_filenames = ddb_doc_entry['image_filenames']
        total_pages = len(image_filenames)
        data = json.loads(dynamoson, parse_float=decimal.Decimal)
        print(f"[{func}] dynamoson: {data}")
        classifications = data['tables']['Document Classifications'][0]['Page Rows']  # list of dicts
        print(f"[DEBUG] classifications: {classifications}")

        if total_pages > len(classifications):
            raise Exception(f"Each page requires it's own classification row! Number of pages: {total_pages}; Submitted Classifications: {len(classifications)}")
        elif total_pages < len(classifications):
            raise Exception(f"More classifications detected than there are pages! Classifications: {len(classifications)}; Pages: {total_pages}")

        ordinal = 1
        for class_dict in classifications:
            print(f"[parsing multiple classification {ordinal}] {class_dict}")

            classification_ = class_dict['doc_type']
            page_range_string = class_dict['page_nums']

            if classification_ is None or (isinstance(classification_, str) and classification_.lower() == "n/a"):
                raise Exception(f"Classification of {classification_} not valid. Please classify the page using the drop-down menu options.")

            stand_success, classification, stand_err = standardize_classification_name(classification_)
            if not stand_success:
                raise Exception(f"standardize_classification_name() >>> {stand_err}")

            success, page_range_dict, err = parse_page_range(page_range=page_range_string, max_pages=total_pages)
            if not success:
                raise Exception(f"parse_page_range() >>> {err}")

            page_res = page_range_dict.copy()
            page_res.update({'classification': classification})

            classification_dict.update({
                str(ordinal): page_res
            })

            ordinal += 1

        # Double-check the data by translating it
        translation_success, translated_data, translation_err = translate_dt_multiclass(
            req_id=req_id,
            data=classification_dict,
            total_pages=total_pages
        )
        if not translation_success:
            anno_errors = [
                "not chronologically related",
                "used more than once",
                "does not match up"
            ]
            for a_err in anno_errors:
                if a_err in translation_err:
                    raise Exception(translation_err)

            raise Exception(f"translate_dt_multiclass() >>> {translation_err}")

        return True, classification_dict, ""

    except Exception as e:
        print(f"[ERROR] {func} Error ==> {e}")
        traceback.print_exc()
        classification_dict.update({
            'error': f"{e}"
        })
        return False, classification_dict, f"{e}"


def translate_dt_multiclass(req_id, data, total_pages) -> tuple[bool, dict, str]:
    """
    Translates the DTs multiclass output into something similar to what the auto-classifier would do if it
    succeeded all the way through; This format has some benefits, such as easily determining if all document pages
    were properly accounted for, as well as translating into other areas such as splitting into separate documents;
    :param req_id:
    :param data:
    :param total_pages:
    :return:
    """
    func = translate_dt_multiclass.__name__
    """
    DT multiclass format:::
    {
        "1": {
                'classification': {doc_class},
                'range_start': int|None,
                'range_end': int|None,
                'singles': list(<int>|empty)
        },
        "2": {
                'classification': {doc_class},
                'range_start': int|None,
                'range_end': int|None,
                'singles': list(<int>|empty)
        },
        etc...
    }
    """
    try:
        page_numbers = list()
        translated = {}
        for num, d, in data.items():

            nums = list()
            if d.get('range_start') is not None and d.get('range_end') is not None:
                nums = [i for i in list(range(int(d['range_start']), int(d['range_end']) + 1))]
            if len(d['singles']) >= 1:
                nums.extend([int(i) for i in d['singles']])

            page_numbers.extend(nums)

            for n in nums:
                if str(n) in translated.keys():
                    raise Exception(f"Page number <{n}> appears to be used more than once! {translated}")

                translated.update({
                    str(n): {
                        "doc_class": d['classification'],
                        "model_class": None
                    }
                })
        page_numbers = sorted(page_numbers)
        first_page = page_numbers[0]
        addition = 1
        for p in page_numbers:
            if page_numbers.index(p) == 0:
                continue
            elif first_page + addition != p:
                raise Exception(f"Flattened page numbers are not chronologically related! page_numbers = {page_numbers}")
            else:
                addition += 1

        if len(page_numbers) != total_pages:
            raise Exception(f"Total number of pages does not match up! Total Pages: {total_pages}; Parsed Annotation Pages: {page_numbers}")

        return True, translated, ""

    except Exception as e:
        print(f"[({req_id}) ERROR] {func} Error ==> {e}")
        traceback.print_exc()
        return False, {}, f"{e}"
