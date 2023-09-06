import json
import traceback
from dukeai_lib.utilities import DecimalEncoder


def get_main_schema():
    schema = {
        "headers": {
            "Header": {
                "file_type": "",
                "uploaded": "",
                "company_name": ""
            }
        },
        "tables": {
            "Item": [
                {
                    "file_type": "",
                    "transactionDate": "",
                    "category": "",
                    "MainCategory": "",
                    "assetType": "",
                    "amount": "",
                    "state": "",
                    "gal": "",
                    "description": ""
                }
            ],
            "Totals": [
                {
                    "net": "",
                    "loss": "",
                    "revenue": ""
                }
            ]
        }
    }
    return schema


def flatten_data_rsi(ddb_obj: dict) -> tuple[bool, dict, str]:
    """
    Takes a DDB object and flattens data into Dynamotator schema;
    :param ddb_obj: dict, DUKE-User-Document object;
    :return: str, flattened schema for Dynamotator UI as json string.
    """
    func = flatten_data_rsi.__name__
    try:
        ddb_copy = ddb_obj.copy()
        auto_ex = ddb_obj.get("autoextracts")
        main_dict = get_main_schema()

        file_type = ddb_obj.get("file_type")
        uploaded = ddb_obj.get("uploaded")
        c_name = ddb_obj.get("company_name")

        main_dict["headers"]["Header"].update({
            "file_type": file_type,
            "uploaded": uploaded,
            "company_name": c_name
        })

        if c_name is None:
            print(f"[WARN] DDB entry has no company_name, unable to locate info in data array; Defaulting to empty schema")
            main_dict["headers"]["Header"].update({"company_name": ""})
            return True, main_dict, "DDB entry has no company_name, unable to locate info in data array; Defaulting to empty schema"

        else:

            if auto_ex is None:
                print(f"[WARN] DDB entry has no autoextracts; Defaulting to empty schema")
                return True, main_dict, "DDB entry has no autoextracts; Defaulting to empty schema"
            else:
                data = auto_ex.get("data")
                if data is None:
                    auto_ex.update({'data': []})
                    data = auto_ex.get("data")

                else:
                    settlement = False
                    key = c_name + "_none"
                    info = data[0].get(key)
                    dat1 = info.get("Invoice")
                    dat2 = info.get("Receipt")
                    if len(dat1) > 0 and len(dat2) > 0:
                        main_dict["headers"]["Header"].update({"file_type": "settlement"})
                        settlement = True

                    if settlement is False:
                        if len(dat1) > 0:  # Invoice
                            dat1 = dat1[0]
                            amount = dat1.get("amount")
                            if amount is not None:
                                amount = float(amount)
                            gal = dat1.get("gal")
                            desc = dat1.get("description")
                            state = dat1.get("state")
                            cat = dat1.get("category")
                            m_cat = dat1.get("MainCategory")
                            date = dat1.get("transactionDate")
                            a_type = dat1.get("assetType")

                            main_dict["tables"]["Item"][0].update({
                                "file_type": file_type,
                                "transactionDate": date,
                                "category": cat,
                                "MainCategory": m_cat,
                                "assetType": a_type,
                                "amount": amount,
                                "state": state,
                                "gal": gal,
                                "description": desc
                            })
                            for k, v in main_dict["tables"]["Item"][0].items():
                                if v is None:
                                    main_dict["tables"]["Item"][0].update({k: ""})
                                else:
                                    continue

                            main_dict["tables"]["Totals"][0].update({
                                "net": amount,
                                "loss": "",
                                "revenue": amount
                            })
                            for k, v in main_dict["tables"]["Totals"][0].items():
                                if v is None:
                                    main_dict["tables"]["Totals"][0].update({k: ""})
                                else:
                                    continue

                            try:
                                flattened_data = json.loads(json.dumps(main_dict, indent=2, cls=DecimalEncoder, separators=(',', ': ')))
                                # flattened_data = json.loads(json.dumps(main_dict, indent=2, parse_floats=Decimal, separators=(',', ': ')))
                                ddb_copy["autoextracts"] = flattened_data
                                return True, ddb_copy, ""
                            except Exception as e:
                                print(f"[FAIL] Dictionary contains characters that are illegal JSON syntax; Defaulting to blank schema; ERROR = {e}")
                                traceback.print_exc()
                                fail = get_main_schema()
                                return False, fail, f"{e}"

                        elif len(dat2) > 0:  # Receipt
                            dat1 = dat2[0]
                            amount = dat1.get("amount")
                            if amount is not None:
                                amount = float(amount)
                            gal = dat1.get("gal")
                            desc = dat1.get("description")
                            state = dat1.get("state")
                            cat = dat1.get("category")
                            m_cat = dat1.get("MainCategory")
                            date = dat1.get("transactionDate")
                            a_type = dat1.get("assetType")

                            main_dict["tables"]["Item"][0].update({
                                "file_type": file_type,
                                "category": cat,
                                "MainCategory": m_cat,
                                "assetType": a_type,
                                "amount": amount,
                                "state": state,
                                "gal": gal,
                                "description": desc
                            })
                            for k, v in main_dict["tables"]["Item"][0].items():
                                if v is None:
                                    main_dict["tables"]["Item"][0].update({k: ""})
                                else:
                                    continue

                            main_dict["tables"]["Totals"][0].update({
                                "net": amount,
                                "loss": "",
                                "revenue": amount
                            })
                            for k, v in main_dict["tables"]["Totals"][0].items():
                                if v is None:
                                    main_dict["tables"]["Totals"][0].update({k: ""})
                                else:
                                    continue

                            try:
                                flattened_data = json.loads(json.dumps(main_dict, indent=2, cls=DecimalEncoder, separators=(',', ': ')))
                                # flattened_data = json.loads(json.dumps(main_dict, indent=2, parse_floats=Decimal, separators=(',', ': ')))
                                ddb_copy["autoextracts"] = flattened_data
                                return True, ddb_copy, ""
                            except Exception as e:
                                print(f"[FAIL] Dictionary contains characters that are illegal JSON syntax; Defaulting to blank schema; ERROR = {e}")
                                traceback.print_exc()
                                fail = get_main_schema()
                                return False, fail, f"{e}"

                    elif settlement is True:
                        print(f"[INFO] settlement is True; passing for now")
                        return True, main_dict, ""

    except Exception as e:
        print(f"[ERROR] {func} Error ==> {e}")
        traceback.print_exc()
        try:
            fail_dict = get_main_schema()
            return False, fail_dict, f"{e}"
        except Exception as ee:
            print(f"[DOUBLE FAIL] {func} failed to generate blank schema; Error ==> {ee}; Original Error ==> {e}")
            traceback.print_exc()
            return False, {}, f"{ee}"
