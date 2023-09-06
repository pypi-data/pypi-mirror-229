import datetime
import json
import re
import traceback
from .schema_utilities import get_idtype, parse_incoming_address, parse_time, format_state


def get_date_schema():
    return {
        "date": None,
        "time": None,
        "datetype": None
    }


def get_reference_schema(idtype):
    _idtype = get_idtype(idtype)
    return {
        "id": None,
        "idtype": idtype,
        "_idtype": _idtype
    }


def get_lineitem_schema():
    return {
        "amount": "0.0",  # Total amount (rate * qty)
        "rate": "0.0",  # Price each
        "qty": "0",
        "id": None  # Name / description
    }


def get_entity_schema(type_):
    func = get_entity_schema.__name__
    try:
        type_code = None
        if type_ == "SHIPPER":
            type_code = "SH"
        elif type_ == "CARRIER":
            type_code = "CR"
        elif type_ == "CONSIGNEE":
            type_code = "CN"
        elif type_ == "BROKER":
            type_code = "BK"
        elif type_ == "BILL TO":
            type_code = "BT"
        elif type_ == "BILL FROM":
            type_code = "BF"

        if type_code is None:
            raise Exception(f"Entity Type <{type_}> not provisioned.")

        return {
            "name": None,
            "type": type_,
            "_type": type_code,
            "id": None,
            "_idtype": "ZZ",
            "address": [],
            "city": None,
            "state": None,
            "postal": None,
            "contacts": {
                "contactname": None,
                "contact_type": None,
                "contact_number": None,
                "contact_number_type": None
            }
        }

    except Exception as e:
        print(f"[ERROR] {func} Error ==> {e}")
        return None


def get_base_invoice_schema():
    return {
        "identifier": None,
        "invoice": {
            "terms": None,
            "total": None,
            "line_items": []
        },
        "dates": [],
        "references": [],
        "entities": []
    }


def get_invoice_fail_schema():
    base = get_base_invoice_schema()
    base['dates'] = [get_date_schema()]
    base['references'] = [get_reference_schema("REFERENCE NUMBER")]
    base['entities'] = [
        get_entity_schema("SHIPPER"),
        get_entity_schema("CONSIGNEE"),
        get_entity_schema("BILL FROM"),
        get_entity_schema("BILL TO")
    ]
    return base


def get_flat_line_item_schema():
    return {
        "amount": None,
        "rate": None,
        "quantity": None,
        "name": None
    }


def get_flat_date_schema():
    return {
        "date_0": None,
        "datetype_0": None,
        "time_0": None
    }


def get_flat_reference_schema(idtype=None):
    return {
        "id": None,
        "idtype": idtype
    }


def get_flat_entity_schema(type_=None):
    return {
        "type": type_,
        "name": None,
        "address": None,
        "city": None,
        "state": None,
        "postal": None,
        "country": None,
        "contactname": None,
        "contact_type": None,
        "contact_number": None,
        "contact_number_type": None
    }


def get_flat_base_schema():
    """
    Flat Invoice Schema.
    """
    return {
        "headers": {
            "General": {
                "identifier": None,
                "terms": None,
                "total": None
            }
        },
        "tables": {
            "General Info": [
                {
                    "Line Items": [],
                    "Document Dates": [],
                    "Document References": [],
                    "Document Entities": []
                }
            ]
        }
    }


def blank_schema():
    base = get_flat_base_schema()
    base['tables']['General Info'][0]['Line Items'] = [get_flat_line_item_schema()]
    base['tables']['General Info'][0]['Document Dates'] = [get_flat_date_schema()]
    base['tables']['General Info'][0]['Document References'] = [get_flat_reference_schema("REFERENCE NUMBER")]
    base['tables']['General Info'][0]['Document Entities'] = [
        get_flat_entity_schema("SHIPPER"),
        get_flat_entity_schema("CONSIGNEE"),
        get_flat_entity_schema("BILL FROM"),
        get_flat_entity_schema("BILL TO")
    ]
    return base


def flatten_invoice(ddb_entry) -> tuple[bool, dict, str]:
    """
    Translate Invoice KVT into Dynamoson.
    """
    func = flatten_invoice.__name__
    try:
        if isinstance(ddb_entry, str):
            ddb_entry = json.loads(ddb_entry)
        ddb_entry = ddb_entry.copy()

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

        main['headers']['General']['identifier'] = data['identifier']
        main['headers']['General']['terms'] = data['invoice']['terms']
        main['headers']['General']['total'] = data['invoice']['total']

        line_items = list()
        for line in data['invoice']['line_items']:
            li = get_flat_line_item_schema()
            li.update({
                "name": line['id'],
                "amount": str(line['amount']),
                "rate": str(line['rate']),
                "quantity": str(line['qty'])
            })
            line_items.append(li)

        if len(line_items) == 0:
            line_items.append(get_flat_line_item_schema())

        main['tables']['General Info'][0]['Line Items'] = line_items

        dates = list()
        for date in data['dates']:
            d = get_flat_date_schema()
            d.update({
                "date_0": date['date'],
                "datetype_0": date['datetype'],
                "time_0": date['time']
            })
            dates.append(d)

        if len(dates) == 0:
            dates.append(get_flat_date_schema())

        main['tables']['General Info'][0]['Document Dates'] = dates

        entities = list()
        for entity in data['entities']:
            ent = get_flat_entity_schema()
            ent.update({
                "type": entity['type'],
                "name": entity['name'],
                "address": entity['address'],
                "city": entity['city'],
                "state": entity['state'],
                "postal": entity['postal'],
                "contactname": entity['contacts']['contactname'],
                "contact_type": entity['contacts']['contact_type'],
                "contact_number": entity['contacts']['contact_number'],
                "contact_number_type": entity['contacts']['contact_number_type']
            })
            entities.append(ent)

        if len(entities) == 0:
            entities.append(get_flat_entity_schema())

        main['tables']['General Info'][0]['Document Entities'] = entities

        references = list()
        for ref in data['references']:
            r = get_flat_reference_schema()
            r.update({
                "id": ref['id'],
                "idtype": ref['idtype']
            })
            references.append(r)

        if len(references) == 0:
            references.append(get_flat_reference_schema())

        main['tables']['General Info'][0]['Document References'] = references

        flattened_data = json.loads(json.dumps(main))
        ddb_entry['autoextracts']['data'] = flattened_data
        return True, ddb_entry, ""

    except Exception as e:
        print(f"[ERROR] {func} Error ==> {e}")
        traceback.print_exc()
        return False, {}, f"{e}"


def unflatten_invoice(dynamoson) -> tuple[bool, dict, str]:
    """
    Translate flattened Invoice data back into original KVT schema.
    """
    func = unflatten_invoice.__name__
    if isinstance(dynamoson, str):
        dynamoson = json.loads(dynamoson)

    try:
        main = get_base_invoice_schema()
        main["identifier"] = dynamoson['headers']['General']['identifier']
        total = dynamoson['headers']['General']['total']
        total = re.sub(r"[^0-9.]+", "", total)
        main['invoice'].update({
            "terms": dynamoson['headers']['General']['terms'],
            "total": total
        })

        line_items = list()
        for line in dynamoson['tables']['General Info'][0]['Line Items']:
            amount = line['amount']
            amount = re.sub(r"[^0-9.]+", "", amount)
            rate = line['rate']
            rate = re.sub(r"[^0-9.]+", "", rate)
            qty = line['quantity']
            qty = re.sub(r"[^0-9.]+", "", qty)
            l = get_lineitem_schema()
            l.update({
                "id": line['name'],
                "amount": amount,
                "rate": rate,
                "qty": qty
            })
            line_items.append(l)

        main['invoice']['line_items'] = line_items

        dates = list()
        for date in dynamoson['tables']['General Info'][0]['Document Dates']:
            d = get_date_schema()

            date_ = date['date_0']
            if date_ is not None:
                date_success, date_, date_err = parse_date(date_str=date_)
                if not date_success:
                    raise Exception(f"Date in Document Dates index {dynamoson['tables']['General Info'][0]['Document Dates'].index(date)} is incorrectly formatted; date={date['date_0']}")

            time_ = date['time_0']
            if time_ is not None:
                time_success, time_, time_err = parse_time(time_str=time_)
                if not time_success:
                    raise Exception(f"Time in Document Dates index {dynamoson['tables']['General Info'][0]['Document Dates'].index(date)} is incorrectly formatted; time={date['time_0']}")

            d.update({
                "date": date_,
                "datetype": date['datetype_0'],
                "time": time_
            })
            dates.append(d)
        main['dates'] = dates

        references = list()
        for ref in dynamoson['tables']['General Info'][0]['Document References']:
            r = get_reference_schema(idtype=ref['idtype'])
            r.update({
                "id": ref['id']
            })
            references.append(r)
        main['references'] = references

        entities = list()
        for ent in dynamoson['tables']['General Info'][0]['Document Entities']:
            entity = get_entity_schema(type_=ent['type'])

            name = ent['name']
            if name is not None:
                name = name.title()

            city = ent['city']
            if city is not None:
                city = city.title()

            state = ent['state']
            if state is not None:
                state_success, state, state_err = format_state(
                    state=state,
                    abbreviate=True
                )
                if not state_success:
                    raise Exception(f"{state_err}")

            address = []
            if ent['address'] is not None:
                address_success, address, address_err = parse_incoming_address(
                    address=ent['address']
                )
                if not address_success:
                    raise Exception(f"parse_incoming_address() >>> {address_err}")
                if bool(re.compile(r"\S+").search(str(address))):
                    address = [address]
                else:
                    address = []

            uid_values = [i for i in [name, city, state, ent['postal']] if i is not None]
            uid_ = "".join(uid_values)
            uid = re.sub('[^A-Za-z0-9]+', '', uid_)
            entity.update({
                "name": name,
                "id": uid,
                "city": city,
                "state": state,
                "postal": ent['postal'],
                "address": address,
                "contacts": {
                    "contactname": ent['contactname'],
                    "contact_type": ent['contact_type'],
                    "contact_number": ent['contact_number'],
                    "contact_number_type": ent['contact_number_type']
                }
            })
            entities.append(entity)
        main['entities'] = entities

        return True, main, ""

    except Exception as e:
        print(f"[ERROR] {func} Error ==> {e}")
        traceback.print_exc()
        return False, {}, f"{e}"


def parse_date(date_str):
    func = parse_date.__name__
    try:
        date_ = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        date_ = date_.strftime('%Y-%m-%d')
        return True, date_, ""
    except Exception as e:
        print(f"[ERROR] {func} Error ==> {e}")
        traceback.print_exc()
        return False, None, f"{e}"


