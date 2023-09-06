import re
import json
import traceback
from .schema_utilities import get_idtype, format_time


"""
The following schemas and translation functions are intended to be used for any document that falls into the 
'Accessorial' category >> Lumper, Drayage, Chassis, & Detention
"""


def get_flat_accessorial_schema():
    schema = {
        "headers": {
            "General": {
                "identifier": "",
                "amount": ""
            }
        },
        "tables": {
            "General Info": [
                {
                    "Document Dates": [],
                    "Document References": []
                }
            ]
        }
    }
    return schema


def get_flat_date_schema():
    return {
        "date_0": "",
        "datetype_0": "",
        "time_0": ""
    }


def get_flat_reference_schema():
    return {
        "id": "",
        "idtype": ""
    }


def blank_schema():
    blank = get_flat_accessorial_schema()
    blank['tables']['General Info'][0].update({
        "Document Dates": [get_flat_date_schema()],
        "Document References": [get_flat_reference_schema()]
    })
    return blank


def flatten_accessorial(ddb_entry) -> tuple[bool, dict, str]:
    """
    Translates an Accessorial document (Lumper, Chassis, Detention, Drayage) KVT into Dynamoson.
    """
    func = flatten_accessorial.__name__
    if isinstance(ddb_entry, str):
        ddb_entry = json.loads(ddb_entry)
    ddb_entry = ddb_entry.copy()
    try:
        auto_ex = ddb_entry.get('autoextracts')

        send_blank = False
        if auto_ex is None:
            print(f"[WARN] 'ddb_entry' has no 'autoextracts' object")
            send_blank = True
        elif auto_ex.get('data') is None:
            print(f"[WARN] 'ddb_entry'[autoextracts] has no 'data' object")
            send_blank = True
        elif len(auto_ex['data'].keys()) == 0:
            print(f"[WARN] 'ddb_entry'[autoextracts][data] has a key-length of 0")
            send_blank = True
        if send_blank:
            ddb_entry.update({
                "autoextracts": {
                    "data": blank_schema()
                }
            })
            return True, ddb_entry, ""

        data = auto_ex["data"]
        main = get_flat_accessorial_schema()

        identifier = str(data['identifier'])
        amount = str(data['amount'])
        amount = re.sub(r"[^\d,.]+", "", amount)
        main["headers"]["General"].update({
            "identifier": identifier,
            "amount": amount
        })

        dates = data.get('dates')
        if len(dates) == 0:
            main["tables"]["General Info"][0].update({
                "Document Dates": [get_flat_date_schema()]
            })
        else:
            for d in dates:
                date_dict = get_flat_date_schema()
                date_dict.update({
                    "date_0": d['date'],
                    "datetype_0": "lumper",
                    "time_0": d['time']
                })
                main["tables"]["General Info"][0]["Document Dates"].append(date_dict)

        references = data.get('references')
        if len(references) == 0:
            main["tables"]["General Info"][0].update({
                "Document References": [get_flat_reference_schema()]
            })
        else:
            for r in references:
                ref_dict = get_flat_reference_schema()
                ref_dict.update({
                    "id": r['id'],
                    "idtype": r['idtype']
                })
                main["tables"]["General Info"][0]["Document References"].append(ref_dict)

        ddb_entry.update({
            "autoextracts": {
                "data": main
            }
        })
        return True, ddb_entry, ""

    except Exception as e:
        print(f"[ERROR] {func} Error ==> {e}")
        traceback.print_exc()
        ddb_entry = ddb_entry.copy()
        ddb_entry.update({
            "autoextracts": {
                "data": blank_schema()
            }
        })
        return False, ddb_entry, f"{e}"


def get_date_schema():
    return {
        "date": None,
        "datetype": None,
        "time": None
    }


def get_reference_schema(idtype):
    _idtype = get_idtype(idtype)
    return {
        "id": None,
        "idtype": idtype,
        "_idtype": _idtype
    }


def get_accessorial_schema():
    return {
        "identifier": None,
        "amount": None,
        "dates": [],
        "references": []
    }


def unflatten_accessorial(dynamoson) -> tuple[bool, dict, str]:
    """
    Translates flattened Accessorial document (Lumper, Chassis, Detention, Drayage) back into KVT schema.
    """
    func = unflatten_accessorial.__name__
    if isinstance(dynamoson, str):
        dynamoson = json.loads(dynamoson)
    try:
        main = get_accessorial_schema()
        identifier = dynamoson["headers"]["General"]["identifier"]
        amount = dynamoson["headers"]["General"]["amount"]
        amount = re.sub(r"[^\d,.]+", "", amount)
        main.update({
            "identifier": identifier,
            "amount": amount
        })

        dates = dynamoson["tables"]["General Info"][0]["Document Dates"]
        if len(dates) == 0:
            raise Exception(f"At least one date object is required for Lumpers")
        else:
            for d in dates:
                date_dict = get_date_schema()
                date_ = d.get('date_0')
                if date_ is None:
                    raise Exception(f"At least one date is required for Lumpers")
                else:
                    if not bool(re.compile(r"\S").search(date_)):
                        raise Exception(f"Incoming date did not contain valid characters; Date={date_}")
                    elif not bool(re.compile(r"(\d{4})-(\d{2})-(\d{2})").search(date_)):
                        raise Exception(f"Incoming date is incorrect format; Date={date_}")
                    d_ = re.compile(r"(\d{4})-(\d{2})-(\d{2})").search(date_)
                    if d_ is None:
                        raise Exception(f"Incoming date is incorrect format; Date={date_}")
                    else:
                        year = int(d_.group(1))
                        if not bool(re.compile(r"20\d{2}").search(str(year))):
                            raise Exception(f"Year is incorrect; Year={year}")
                        month = int(d_.group(2))
                        if month > 12:
                            raise Exception(f"Month is greater than 12; Month={month}")
                        day = int(d_.group(3))
                        if day > 31:
                            raise Exception(f"Day is greater than 31; Day={day}")

                time = d.get('time_0')
                if time is not None:
                    if bool(re.compile(r"\S").search(time)):
                        time_success, time, time_err = format_time(time)
                        if not time_success:
                            raise Exception(f"format_time() >>> {time_err}")
                        time = time.strftime('%H:%M')
                    else:
                        time = None
                date_dict.update({
                    'date': date_,
                    'time': time,
                    'datetype': 'lumper'
                })
                main['dates'].append(date_dict)

        references = dynamoson["tables"]["General Info"][0]["Document References"]
        if len(references) == 0:
            print(f"No incoming lumper references; skipping...")
        else:
            for r in references:
                idtype = r.get("idtype")
                ref_dict = get_reference_schema(idtype=idtype)
                ref_dict.update({
                    "id": r.get("id")
                })
                main['references'].append(ref_dict)

        print(f"TRANSLATED ASSESSORIAL = {json.dumps(main)}")
        return True, main, ""

    except Exception as e:
        print(f"[ERROR] {func} Error ==> {e}")
        traceback.print_exc()
        return False, {}, f"{e}"
