# noa_lor_flattener.py
import json
import traceback
from dukeai_lib.utilities import DecimalEncoder


def get_main_schema():
    main_schema = {
        "headers": {
            "General": {},
            "NOA Information": {},
            "LOR Information": {}
        },
        "tables": {}
    }
    return main_schema


def get_general_schema():
    schema = {
        "broker_id": "",
        "carrier_name": "",
        "carrier_mc_no": "",
        "date": "",
        "broker_name": ""
    }
    return schema


def get_noa_schema():
    schema = {
        "noa_factoring_company_id": "",
        "noa_factoring_company_name": "",
        "noa_page_number": ""
    }
    return schema


def get_lor_schema():
    schema = {
        "lor_factoring_company_id": "",
        "lor_factoring_company_name": "",
        "lor_page_number": ""
    }
    return schema


def fail_schema():
    main = dict(get_main_schema())
    main["headers"].update({
        "General": dict(get_general_schema()),
        "NOA Information": dict(get_noa_schema()),
        "LOR Information": dict(get_lor_schema())
    })
    return main


def flatten_noa_lor(ddb_obj: dict) -> tuple[bool, dict, str]:
    """
    Takes a DDB object and flattens data into Dynamotator schema;
    :param ddb_obj: dict, DUKE-User-Document object;
    :return: str, flattened schema for Dynamotator UI.
    """
    # known special characters to remove that don't play nicely with JSON
    func = flatten_noa_lor.__name__
    char_dict = r"\"|\'|\x0c"
    print(f"[INFO] {func} activated")
    try:
        print(f"[INCOMING DDB OBJECT] {ddb_obj}")
        ddb_copy = ddb_obj.copy()
        auto_ex = ddb_obj.get("autoextracts")

        if auto_ex is None:
            print(f"[WARN] DDB entry has no autoextracts; Defaulting to empty schema")
            ddb_copy["autoextracts"]["data"] = fail_schema()
            return True, ddb_copy, ""

        else:
            data = auto_ex.get("data")
            if data is None or (isinstance(data, dict) and len(data.keys()) == 0):
                print(f"[WARN] autoextracts has no data object; Defaulting to empty schema")
                ddb_copy["autoextracts"]["data"] = fail_schema()
                return True, ddb_copy, ""

            else:
                empty = True
                for k, v in data.items():
                    if v is not None:
                        empty = False
                if empty:
                    print(f"[WARN] No data found in Autoextracts, checking Extracts....")
                    data = ddb_obj.get("extracts")
                    if isinstance(data, dict):
                        if 'data' in data.keys():
                            data = data['data']
                            for k, v in data.items():
                                if v is not None:
                                    empty = False
                if empty:
                    print(f"[WARN] Data is empty in Extracts AND Autoextracts")
                    ddb_copy["autoextracts"]["data"] = fail_schema()
                    return True, ddb_copy, "Data is empty in Extracts AND Autoextracts"

                main = get_main_schema()
                main_headers = dict(main["headers"])
                general = get_general_schema()
                date = data.get("date")
                cname = data.get("carrier_name")
                cmc = data.get("carrier_mc_no")
                bid = data.get("broker_id")
                bname = data.get("broker_name")
                general.update({
                    "broker_id": bid,
                    "carrier_name": cname,
                    "carrier_mc_no": cmc,
                    "date": date,
                    "broker_name": bname
                })
                for k, v in general.items():
                    if v is None:
                        general.update({k: ""})
                    else:
                        pass
                main_headers.update({"General": general})
                print(f"[DEBUG] general = {general}")

                noa = get_noa_schema()
                nfc_id = data.get("noa_factoring_company_id")
                nfc_name = data.get("noa_factoring_company_name")
                n_pn = data.get("noa_page_number")
                noa.update({
                    "noa_factoring_company_id": nfc_id,
                    "noa_factoring_company_name": nfc_name,
                    "noa_page_number": n_pn
                })
                for k, v in noa.items():
                    if v is None:
                        noa.update({k: ""})
                    else:
                        pass
                main_headers.update({"NOA Information": noa})
                print(f"[DEBUG] noa = {noa}")

                lor = get_lor_schema()
                lfc_id = data.get("lor_factoring_company_id")
                lfc_name = data.get("lor_factoring_company_name")
                l_pn = data.get("lor_page_number")
                lor.update({
                    "lor_factoring_company_id": lfc_id,
                    "lor_factoring_company_name": lfc_name,
                    "lor_page_number": l_pn
                })
                for k, v in lor.items():
                    if v is None:
                        lor.update({k: ""})
                    else:
                        pass
                main_headers.update({"LOR Information": lor})
                print(f"[DEBUG] lor = {lor}")

                main["headers"] = main_headers

                try:
                    flattened_data = json.loads(json.dumps(main, indent=2, cls=DecimalEncoder, separators=(',', ': ')))
                    ddb_copy["autoextracts"]["data"] = flattened_data
                    print("[INFO] flatten_noa_lor() completed")
                    return True, ddb_copy, ""
                except Exception as ee:
                    print(f"[FAIL] Dictionary contains characters that are illegal JSON syntax; Defaulting to blank schema; ERROR = {ee}")
                    ddb_copy["autoextracts"]["data"] = fail_schema()
                    return True, ddb_copy, f"{ee}"

    except Exception as e:
        print(f"[ERROR] {func} failed; Error ==> {e}")
        traceback.print_exc()
        try:
            ddb_copy = ddb_obj.copy()
            ddb_copy["autoextracts"]["data"] = fail_schema()
            return False, ddb_copy, f"{e}"
        except Exception as eee:
            print(f"[DOUBLE FAIL] flatten_data for (noa_lor) failed to generate blank schema to return; ERROR = {eee}")
            traceback.print_exc()
            return False, {}, f"{eee}"


def get_noa_lor_schema():
    schema = {
        "date": None,
        "carrier_name": None,
        "carrier_mc_no": None,
        "noa_factoring_company_name": None,
        "lor_factoring_company_name": None,
        "noa_page_number": None,
        "lor_page_number": None
    }
    return schema


def unflatten_noa_lor(flattened_ddb_entry: str) -> tuple[bool, dict, str]:
    """
    Takes flattened data from the Dynamotator UI and rebuilds the information into the original Schema;
    :param flattened_ddb_entry: JSON str;
    :return: JSON str, Original ratecon schema inside the ddb_entry.
    """
    func = unflatten_noa_lor.__name__
    if isinstance(flattened_ddb_entry, dict):
        flattened_ddb_entry = json.dumps(flattened_ddb_entry)

    data = json.loads(flattened_ddb_entry)
    # data = data['autoextracts']['data']

    main = get_noa_lor_schema()
    try:
        general = data["headers"].get("General")
        date = general.get("date")
        carrier_name = general.get("carrier_name")
        carrier_mc_no = general.get("carrier_mc_no")
        main.update({
            "date": date,
            "carrier_name": carrier_name,
            "carrier_mc_no": carrier_mc_no
        })

        noa = data["headers"].get("NOA Information")
        noa_factoring_company_name = noa.get("noa_factoring_company_name")
        noa_page_number = noa.get("noa_page_number")
        main.update({
            "noa_factoring_company_name": noa_factoring_company_name,
            "noa_page_number": noa_page_number
        })

        lor = data["headers"].get("LOR Information")
        lor_factoring_company_name = lor.get("lor_factoring_company_name")
        lor_page_number = lor.get("lor_page_number")
        main.update({
            "lor_factoring_company_name": lor_factoring_company_name,
            "lor_page_number": lor_page_number
        })

        return True, main, ""

    except Exception as e:
        print(f"[ERROR] {func} Error ==> {e}")
        traceback.print_exc()
        return False, {}, f"{e}"
