import re
import json
import traceback
from .schema_utilities import get_idtype, format_time, format_state


def get_flat_entity_schema():
    return {
        "type": None,
        "name": None,
        "address": None,
        "city": None,
        "state": None,
        "postal": None,
        "country": None,
        "contactname": None,
        "contact_number": None
    }


def get_flat_date_schema():
    return {
        "date_0": None,
        "datetype_0": None,
        "time_0": None
    }


def get_flat_reference_schema():
    return {
        "id": None,
        "idtype": None
    }


def get_flat_base_schema():
    return {
        "headers": {
            "General": {
                "identifier": None,
                "delivery_signature": False,
                "is_delivered": False,
                "charges": None
            }
        },
        "tables": {
            "General Info": [
                {
                    "Document Dates": [],
                    "Document References": [],
                    "Document Entities": []
                }
            ]
        }
    }


def blank_schema():
    blank = get_flat_base_schema()
    consignee_entity = get_flat_entity_schema()
    consignee_entity.update({'type': 'CONSIGNEE'})
    shipper_entity = get_flat_entity_schema()
    shipper_entity.update({'type': 'SHIPPER'})
    carrier_entity = get_flat_entity_schema()
    carrier_entity.update({'type': 'CARRIER'})

    shipped_date = get_flat_date_schema()
    shipped_date.update({'datetype_0': 'General'})
    delivered_date = get_flat_date_schema()
    delivered_date.update({'datetype_0': 'Delivered'})

    blank['tables']['General Info'][0].update({
        "Document Dates": [shipped_date, delivered_date],
        "Document References": [get_flat_reference_schema()],
        "Document Entities": [consignee_entity, shipper_entity, carrier_entity]
    })
    return blank


def flatten_bol(ddb_entry) -> tuple[bool, dict, str]:
    """
    Translates the BOL KVT into Dynamoson.
    """
    func = flatten_bol.__name__
    if isinstance(ddb_entry, str):
        ddb_entry = json.loads(ddb_entry)
    ddb_entry = ddb_entry.copy()
    try:
        send_blank = False
        auto_ex = ddb_entry.get('autoextracts')

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
            blank = blank_schema()
            ddb_entry.update({
                "autoextracts": {
                    "data": blank
                }
            })
            return True, ddb_entry, ""

        ### Begin mapping data from the KVT to the Dynamoson
        data = auto_ex["data"]
        main = get_flat_base_schema()

        identifier = str(data['identifier'])
        del_sig = data["delivery_signature"]
        if isinstance(del_sig, str):
            if del_sig.lower() == "true":
                del_sig = True
            elif del_sig.lower() == "false":
                del_sig = False
        is_delivered = data["is_delivered"]
        if isinstance(is_delivered, str):
            if is_delivered.lower() == "true":
                is_delivered = True
            elif is_delivered.lower() == "false":
                is_delivered = False
        charges = str(data["charges"])

        main["headers"]["General"].update({
            "identifier": identifier,
            "delivery_signature": del_sig,
            "is_delivered": is_delivered,
            "charges": charges
        })

        dates = data["dates"]
        shipped_date = False
        delivered_date = False
        for d in dates:
            date_dict = get_flat_date_schema()

            if not bool(re.compile(r"\S").search(d['date'])):
                print("Skipping blank date dict...")
                continue

            if d.get('datetype') is not None:
                datetype = d['datetype']
                if datetype.lower() in ["shipped", "general"]:
                    shipped_date = True
                elif datetype.lower() == "delivered":
                    delivered_date = True

            date_dict.update({
                "date_0": d["date"],
                "datetype_0": d["datetype"],
                "time_0": d["time"]
            })
            main["tables"]["General Info"][0]["Document Dates"].append(date_dict)
        if not shipped_date:
            shipped_date_ = get_bol_date_schema()
            shipped_date_.update({'datetype_0': 'General'})
            main["tables"]["General Info"][0]["Document Dates"].append(shipped_date_)
        if not delivered_date:
            delivered_date_ = get_bol_date_schema()
            delivered_date_.update({'datetype_0': 'Delivered'})
            main["tables"]["General Info"][0]["Document Dates"].append(delivered_date_)

        references = data["references"]
        for r in references:

            if not bool(re.compile(r"\S").search(r['id'])):
                print("Skipping blank date dict...")
                continue

            ref = get_flat_reference_schema()
            ref.update({
                "id": r["id"],
                "idtype": r["idtype"]
            })
            main["tables"]["General Info"][0]["Document References"].append(ref)
        if len(main["tables"]["General Info"][0]["Document References"]) == 0:
            ref_ = get_flat_reference_schema()
            main["tables"]["General Info"][0]["Document References"].append(ref_)

        entities = data["entities"]
        consignee = False
        shipper = False
        carrier = False
        for e in entities:
            ent = get_flat_entity_schema()

            if e.get('type') is not None:
                ent_type = e['type']
                if ent_type.lower() == "consignee":
                    consignee = True
                elif ent_type.lower() == "shipper":
                    shipper = True
                elif ent_type.lower() == "carrier":
                    carrier = True

            ent.update({
                "name": e["name"],
                "type": e["type"],
                "city": e["city"],
                "state": e["state"],
                "postal": e["postal"],
                "country": e["country"],
                "contactname": e["contacts"]["contactname"],
                "contact_type": e["contacts"]["contact_type"],
                "contact_number": e["contacts"]["contact_number"],
                "contact_number_type": e["contacts"]["contact_number_type"]
            })
            address = None
            address_ = e["address"]
            if isinstance(address_, str):
                address = address_.upper()
            elif isinstance(address_, list):
                address = list()
                for a in address_:
                    if isinstance(a, str):
                        address.append(a.upper())
                    elif isinstance(a, list):
                        for aa in a:
                            address.append(aa.upper())
                address = " ".join(address)

            ent["address"] = address
            main["tables"]["General Info"][0]["Document Entities"].append(ent)

        if not shipper:
            shipper_ = get_flat_entity_schema()
            shipper_.update({'type': 'SHIPPER'})
            main["tables"]["General Info"][0]["Document Entities"].append(shipper_)
        if not consignee:
            consignee_ = get_flat_entity_schema()
            consignee_.update({'type': 'CONSIGNEE'})
            main["tables"]["General Info"][0]["Document Entities"].append(consignee_)
        if not carrier:
            carrier_ = get_flat_entity_schema()
            carrier_.update({'type': 'CARRIER'})
            main["tables"]["General Info"][0]["Document Entities"].append(carrier_)

        try:
            flattend_data = json.loads(json.dumps(main))
            ddb_entry['autoextracts']['data'] = flattend_data
            print(f"[FLATTENED DATA] {flattend_data}")
            return True, ddb_entry, ""
        except Exception as ee:
            print(f"[WARN] Could not dump and load flattened data ==> {ee}")
            blank = blank_schema()
            ddb_entry.update({
                "autoextracts": {
                    "data": blank
                }
            })
            return True, ddb_entry, f"{ee}"

    except Exception as e:
        print(f"[ERROR] {func} Error ==> {e}")
        traceback.print_exc()
        blank = blank_schema()
        ddb_entry.update({
            "autoextracts": {
                "data": blank
            }
        })
        return False, ddb_entry, f"{e}"


def get_bol_reference_schema(idtype):
    _idtype = get_idtype(idtype)
    return {
        "id": None,
        "idtype": idtype,
        "_idtype": _idtype
    }


def get_bol_date_schema():
    return {
        "date": None,
        "datetype": None,
        "time": None
    }


def get_bol_entity_schema(type_):
    func = get_bol_entity_schema.__name__
    _type = None
    if type_.upper() == "SHIPPER":
        _type = "SH"
    elif type_.upper() == "CONSIGNEE":
        _type = "CN"
    elif type_.upper() == "CARRIER":
        _type = "CR"
    elif type_.upper() == "BILL TO":
        _type = "BT"
    elif type_.upper() == "BROKER":
        _type = "BK"
    else:
        print(f"[WARN][{func}] {type_} unable to be matched to type-code.")
    return {
        "name": None,
        "type": type_.upper(),
        "_type": _type,
        "city": None,
        "state": None,
        "postal": None,
        "country": None,
        "address": [],
        "contacts": {
            "contactname": None,
            "contact_type": None,
            "contact_number": None,
            "contact_number_type": None
        }
    }


def get_bol_schema():
    return {
        "identifier": None,
        "delivery_signature": False,
        "is_delivered": False,
        "charges": None,
        "dates": [],
        "references": [],
        "entities": []
    }


def unflatten_bol(dynamoson) -> tuple[bool, dict, str]:
    """
    Translate flattened BOL data back into the KVT schema
    """
    func = unflatten_bol.__name__
    if isinstance(dynamoson, str):
        dynamoson = json.loads(dynamoson)

    try:
        main = get_bol_schema()
        general = dynamoson["headers"]["General"]
        identifier = general["identifier"]
        delivery_signature = general["delivery_signature"]
        if isinstance(delivery_signature, str):
            if delivery_signature.lower() in ["true", "yes", "y"]:
                delivery_signature = True
            elif delivery_signature.lower() in ["false", "no", "n"]:
                delivery_signature = False
        is_delivered = general["is_delivered"]
        if isinstance(is_delivered, str):
            if is_delivered.lower() in ["true", "yes", "y"]:
                is_delivered = True
            elif is_delivered.lower() in ["false", "no", "n"]:
                is_delivered = False
        charges = str(general["charges"])
        charges = re.sub(r"[^\d.]+", "", charges)

        main.update({
            "identifier": identifier,
            "delivery_signature": delivery_signature,
            "is_delivered": is_delivered,
            "charges": charges
        })

        dates = dynamoson["tables"]["General Info"][0]["Document Dates"]
        shipped_date = False
        delivered_date = False
        for d in dates:
            if d['date_0'] is None:
                continue
            if not bool(re.compile(r"\S+").search(d['date_0'])):
                continue
            if not bool(re.compile(r"\d{4}-\d{2}-\d{2}").search(d['date_0'])):
                raise Exception(f"Date {d['date_0']} is improperly formatted")

            date_dict = get_bol_date_schema()
            date = d["date_0"]
            time = d["time_0"]
            if time is not None:
                if bool(re.compile(r"\S").search(time)):
                    time_success, time, time_err = format_time(time)
                    if not time_success:
                        raise Exception(f"format_time() >>> {time_err}")
                    time = time.strftime('%H:%M')
                else:
                    time = None
            else:
                time = None

            if d.get("datetype_0") is None:
                raise Exception(f"{d['date_0']} had a datetype of {d['datetype_0']} submitted. A valid datetype must be selected.")
            if d["datetype_0"].upper() in ["GENERAL", "SHIPPED"]:
                shipped_date = True
            elif d["datetype_0"].upper() == "DELIVERED":
                delivered_date = True

            date_dict.update({
                "date": date,
                "datetype": d["datetype_0"].upper(),
                "time": time
            })
            main["dates"].append(date_dict)

        if not shipped_date:
            print(f"[WARN] No shipping date found!")
            return False, {}, "Shipment or General Document date required"

        elif not delivered_date and (is_delivered is True or delivery_signature is True):
            print(f"[WARN] If shipment has been delivered or has signature, then delivery date is required")
            return False, {}, "If shipment has been delivered or has signature, then delivery date is required"

        references = dynamoson["tables"]["General Info"][0]["Document References"]
        for r in references:
            if r['id'] is None:
                continue
            if not bool(re.compile(r"\S+").search(r['id'])):
                continue
            if r.get('idtype') is None:
                raise Exception(f"{r['id']} had an idtype of {r['idtype']} submitted. A valid idtype must be selected.")

            ref = get_bol_reference_schema(idtype=r["idtype"])
            id_ = r["id"]
            ref.update({
                "id": id_
            })
            main["references"].append(ref)

        entities = dynamoson["tables"]["General Info"][0]["Document Entities"]
        carrier = False
        for e in entities:
            if e.get('type') is None:
                raise Exception(f"Entity {e['name']} had a type of {e['type']} submitted. A valid type must be selected.")
            if e["type"] == "CARRIER":
                carrier = True
            ent = get_bol_entity_schema(type_=e["type"])
            name = e["name"]
            if name is not None:
                name = name.upper()
            city = e["city"]
            if city is not None:
                city = city.upper()
            state = e["state"]
            if state is not None:
                state_success, state, state_err = format_state(state=state, abbreviate=True)
                if not state_success:
                    raise Exception(f"format_state() >>> {state_err}")

            country = e.get("country")
            if country is not None:
                country = country.upper()
            address = e["address"]
            if address is not None:
                address = address.upper()
            postal = e["postal"]
            if postal is not None:
                postal = str(postal)

            contactname = e["contactname"]
            if contactname is not None:
                contactname = contactname.upper()
            contact_type = e.get("contact_type")
            if contact_type is not None:
                contact_type = contact_type.upper()
            contact_number = e["contact_number"]
            if contact_number is not None:
                contact_number = contact_number.upper()
            contact_number_type = e.get("contact_number_type")
            if contact_number_type is not None:
                contact_number_type = contact_number_type.upper()

            ent.update({
                "name": name,
                "city": city,
                "state": state,
                "country": country,
                "postal": postal,
                "address": [address],
                "contacts": {
                    "contactname": contactname,
                    "contact_type": contact_type,
                    "contact_number": contact_number,
                    "contact_number_type": contact_number_type
                }
            })
            main["entities"].append(ent)

        if carrier is False:
            print(f"[FAIL] Carrier not found!")
            return False, main, "Carrier is a required entity"

        return True, main, ""

    except Exception as e:
        print(f"[ERROR] {func} ==> {e}")
        traceback.print_exc()
        return False, {}, f"{e}"
