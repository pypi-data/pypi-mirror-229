import json
import traceback
import re
import datetime
from dukeai_lib.utilities import DecimalEncoder
from .schema_utilities import get_idtype, REFERENCE_OPTIONS, STATES


def get_main_schema():
    main_schema = {
        "headers": {
            "General": {},
            "Broker Details": {},
        },
        "tables": {
            "General Info": [
                {
                    "Document Dates": [],
                    "Shipment Details": [],
                    "Document References": [],
                    "Document Notes": []
                }
            ],
            "Stops": []
        }
    }
    return main_schema


def get_flat_stop_schema():
    # main_schema >> Stops
    stop_schema = {
        "Stop Type": [],
        "Dates": [],
        "Entity": [],
        "References": [],
        "Order Detail": [],
        "Notes": []
    }
    return stop_schema


def get_general_info():
    # main_schema >> headers >> General
    general_info = {
        "identifier": "",
        "identifier_type": "ID Number",
        "client": "",
        "sender": "",
        "receiver": "",
        "isa_ID": ""
    }
    return general_info


def get_entity():
    # main_schema >> headers >> Broker Details
    # stop_schema >> Entity
    entity = {
        "type": "",
        "_type": "",
        "name": "",
        "contactname": "",
        "contact_number": "",
        "contact_type": "",  # Non-rendering
        "contact_number_type": "",  # Non-rendering
        "address": [],
        "city": "",
        "state": "",
        "postal": ""
    }
    return entity


def get_stoptype():
    # stop_schema >> Stop Type
    stop_type = {
        "stoptype": "",
        "_stoptype": "",
        "ordinal": ""  # non-rendering // integer
    }
    return stop_type


def get_date():
    # main_schema >> tables >> General Info >> Document Dates
    # stop_schema >> Dates
    dates = {
        "date_0": "",  # yyyy-mm-dd earliest
        "time_0": "",  # 00:00 earliest
        "date_1": "",  # yyyy-mm-dd latest
        "time_1": "",  # 00:00 latest
        "datetype_0": "",  # Non-rendering
        "timetype_0": "",  # Non-rendering
        "datetype_1": "",  # Non-rendering
        "timetype_1": ""  # Non-rendering
    }
    return dates


def get_shipment():
    # main_schema >> tables >> General Info >> Shipment Details
    shipment = {
        "equipment_number": "",
        "distance": "",
        "weight": "",
        "weight_unit_code": "LBS.",
        "weight_qualifier": "",
        "volume": "",
        "volume_qualifier": "",
        "truck_type": "",
        "temperature": "",
        "trucklength": "",
        "charges": "",
        "loading_quantity": ""
    }
    return shipment


def get_reference():
    # main_schema >> tables >> General Info >> Document References
    # stop_schema >> References
    reference = {
        "id": "",
        "_idtype": "",
        "idtype": ""  # Non-rendering
    }
    return reference


def get_note():
    # main_schema >> tables >> General Info >> Document Notes
    # stop_schema >> Notes
    note = {
        "note": "",
        "notetype": "",  # Non-rendering
        "_notetype": ""  # Non-rendering
    }
    return note


def get_purchase_order():
    # stop_schema >> Order Detail
    purchase_order = {
        "purchase_order_number": "",
        "date": "",
        "cases": "",
        "weight": "",
        "weight_unit_code": "",
        "volume_type": "",
        "volume_units": ""
    }
    return purchase_order


def create_blank_stop(stop_type: str, ordinal: int):
    try:
        stop_dict = get_flat_stop_schema()
        stop_type_dict = dict(get_stoptype())
        if stop_type.lower() == "pick":
            stop_type_dict.update({"stoptype": "PICK"})
            stop_type_dict.update({"ordinal": ordinal})
        elif stop_type.lower() == "drop":
            stop_type_dict.update({"stoptype": "DROP"})
            stop_type_dict.update({"ordinal": ordinal})
        stop_dict["Stop Type"].append(stop_type_dict)
        stop_dict["Dates"].append(get_date())
        entity = get_entity()
        if stop_type.lower() == "pick":
            entity.update({'type': 'SHIPPER'})
        if stop_type.lower() == "drop":
            entity.update({'type': 'CONSIGNEE'})
        stop_dict["Entity"].append(entity)
        stop_dict["References"].append(get_reference())
        stop_dict["Order Detail"].append(get_purchase_order())
        stop_dict["Notes"].append(get_note())
        return stop_dict
    except Exception as e:
        print(e)
        stop_dict = get_flat_stop_schema()
        stop_type_dict = get_stoptype()
        stop_dict["Stop Type"].append(stop_type_dict)
        stop_dict["Dates"].append(get_date())
        stop_dict["Entity"].append(get_entity())
        stop_dict["References"].append(get_reference())
        stop_dict["Order Detail"].append(get_purchase_order())
        stop_dict["Notes"].append(get_note())
        return stop_dict


def fail_schema():
    main_dict = get_main_schema()
    broker = get_entity()
    broker.update({'type': 'BROKER'})
    main_dict["headers"].update({"General": dict(get_general_info()), "Broker Details": dict(broker)})
    general = main_dict["tables"]["General Info"][0]
    general["Document Dates"].append(get_date())
    general["Shipment Details"].append(get_shipment())
    general["Document References"].append(get_reference())
    general["Document Notes"].append(get_note())
    stops = main_dict["tables"]["Stops"]
    pick = create_blank_stop("PICK", 1)
    stops.append(pick)
    drop = create_blank_stop("DROP", 2)
    stops.append(drop)

    return main_dict


def flatten_rate_confirmation(ddb_obj: dict) -> tuple[bool, dict, str]:
    """
    Takes a DDB object and flattens data into Dynamotator schema.
    :param ddb_obj: dict, DUKE-User-Document object.
    :return: str, flattened schema for Dynamotator UI as json string.
    """
    # known special characters to remove that don't play nicely with JSON
    func = flatten_rate_confirmation.__name__
    char_dict = r"\"|\'|\x0c"
    ref_options = list(REFERENCE_OPTIONS.keys())
    try:
        # ddb_obj = json.loads(ddb_str)
        ddb_copy = ddb_obj.copy()
        auto_ex = ddb_obj.get("autoextracts")

        if auto_ex is None:
            print(f"[WARN] DDB entry has no autoextracts; Defaulting to empty schema")
            main_dict = fail_schema()
            return True, main_dict, ""

        else:
            data = auto_ex.get("data")
            if data is None:
                main_dict = get_main_schema()
                general_info = get_general_info()
                auto_ex.update({'data': {}})
                data = auto_ex.get("data")
            else:
                main_dict = get_main_schema()
                # main_dict >> headers >> General
                general_info = get_general_info()
                sender = data.get("sender")
                client = data.get("client")
                receiver = data.get("receiver")
                if receiver is None:
                    data.update({
                        "receiver": {
                            "name": "",
                            "isa_qual": "ZZ",
                            "isa_ID": ""
                        }
                    })
                    receiver = data.get("receiver")
                rec_name = receiver.get("name")

                isa_id = receiver.get("isa_ID")

                identifier = data.get("identifier")
                identifier_type = data.get("identifier_type")
                general_info.update({
                    "identifier": identifier,
                    # "identifier_type": identifier_type,
                    "client": client,
                    "sender": sender,
                    "receiver": rec_name,
                    "isa_ID": isa_id
                })

                for k, v in general_info.items():
                    if v is None:
                        general_info.update({k: ""})

            main_dict["headers"].update({"General": dict(general_info)})
            # main_dict >> headers >> Broker Details
            broker = False
            broker_index = 0
            broker_info = get_entity()
            entities = data.get("entities")
            if entities is None:
                print(f"[INFO] No entities found for this document.")
                broker = False

            else:
                for ent in entities:
                    type_ = ent.get("type")
                    if type_.lower() != "broker":
                        name = ent.get("name")
                        print(f"[INFO] Passing over entity ({name}) of type ({type_}), only looking for broker")

                    else:
                        broker_index = entities.index(ent)
                        broker = True

            if broker is False:
                for k, v in broker_info.items():
                    if isinstance(v, list):
                        if len(v) == 0:
                            broker_info.update({k: [""]})

                    elif v is None:
                        broker_info.update({k: ""})

                main_dict["headers"].update({"Broker Details": dict(broker_info)})
                print("[WARN] could not find broker")

            else:
                entity = entities[broker_index]
                contactname = ""
                contact_number = ""
                contact_type = ""
                contact_number_type = ""
                name = entity.get("name")
                city = entity.get("city")
                state = entity.get("state")
                postal = entity.get("postal")
                address = entity.get("address")
                contacts = entity.get("contacts")
                if contacts is not None:
                    contactname = contacts.get("contactname")
                    contact_number = contacts.get("contact_number")
                    contact_type = contacts.get("contact_type")
                    contact_number_type = contacts.get("contact_number_type")

                broker_info.update({
                    "name": name,
                    "contactname": contactname,
                    "contact_number": contact_number,
                    "contact_number_type": contact_number_type,  # non-rendering
                    "contact_type": contact_type,  # non-rendering
                    "city": city,
                    "state": state,
                    "postal": postal,
                    "type": "BROKER"
                })
                if isinstance(broker_info["address"], list):
                    if len(address) > 1:
                        broker_info["address"] = []
                        for i in address:
                            if isinstance(i, list):
                                i = "".join(i)
                            i = re.sub(char_dict, "", i)
                            broker_info["address"].append(i)
                    elif len(address) == 1:
                        broker_info["address"] = []
                        if isinstance(address[0], list):
                            address[0] = "".join(address[0])
                        ii = re.sub(char_dict, "", address[0])
                        broker_info["address"].append(ii)
                else:
                    print(f"[WARN] Extracted type of address is not list; address = {address}")

                for k, v in broker_info.items():
                    if isinstance(v, list):
                        if len(v) == 0:
                            broker_info.update({k: []})

                    elif v is None:
                        broker_info.update({k: ""})

            main_dict["headers"].update({"Broker Details": dict(broker_info)})
            general = main_dict["tables"]["General Info"][0]

            # main_dict >> tables >> General Info >> Document Dates
            doc_dates = get_date()
            main_dates = data.get("dates")
            if main_dates is None:
                for k, v in doc_dates.items():
                    if v is None:
                        doc_dates.update({k: ""})

                general["Document Dates"].append(doc_dates)
            elif len(main_dates) == 1:
                date = main_dates[0].get("date")
                time = main_dates[0].get("time")
                datetype_0 = main_dates[0].get("datetype")  # non-rendering
                timetype_0 = main_dates[0].get("timetype")  # non-rendering
                doc_dates.update({
                    "date_0": date,
                    "time_0": time,
                    "datetype_0": datetype_0,  # non-rendering
                    "timetype_0": timetype_0  # non-rendering
                })
                for k, v in doc_dates.items():
                    if v is None:
                        doc_dates.update({k: ""})

                general["Document Dates"].append(doc_dates)
            elif len(main_dates) == 2:
                date1 = main_dates[0].get("date")
                time1 = main_dates[0].get("time")
                datetype_0 = main_dates[0].get("datetype")  # non-rendering
                timetype_0 = main_dates[0].get("timetype")  # non-rendering
                date2 = main_dates[1].get("date")
                time2 = main_dates[1].get("time")
                datetype_1 = main_dates[1].get("datetype")  # non-rendering
                timetype_1 = main_dates[1].get("timetype")  # non-rendering
                doc_dates.update({
                    "date_0": date1,
                    "time_0": time1,
                    "datetype_0": datetype_0,  # non-rendering
                    "timetype_0": timetype_0,  # non-rendering
                    "date_1": date2,
                    "time_1": time2,
                    "datetype_1": datetype_1,  # non-rendering
                    "timetype_1": timetype_1  # non-rendering
                })
                for k, v in doc_dates.items():
                    if v is None:
                        doc_dates.update({k: ""})

                general["Document Dates"].append(doc_dates)

            if len(general["Document Dates"]) < 1:
                doc_dates_ = get_date()
                general["Document Dates"].append(doc_dates_)

            # main_dict >> tables >> General Info >> Shipment Details
            shipment = get_shipment()
            main_shipment_details = data.get("shipment")
            if main_shipment_details is None:
                print(f"[INFO] No shipment data key found...is this document completely unclassified? Appending blank shipment schema.")
                general["Shipment Details"].append(shipment)

            else:
                distance = main_shipment_details.get("distance")
                equipment_number = main_shipment_details.get("equipment_number")
                weight = main_shipment_details.get("weight")
                weight_unit_code = main_shipment_details.get("weight_unit_code")
                weight_qualifier = main_shipment_details.get("weight_qualifier")
                volume = main_shipment_details.get("volume")
                volume_qualifier = main_shipment_details.get("volume_qualifier")
                truck_type = main_shipment_details.get("truck_type")
                temperature = main_shipment_details.get("temperature")
                trucklength = main_shipment_details.get("trucklength")
                charges = main_shipment_details.get("charges")
                loading_quantity = main_shipment_details.get("loading_quantity")
                shipment.update({
                    "equipment_number": equipment_number,
                    "distance": distance,
                    "weight": weight,
                    # "weight_unit_code": weight_unit_code,
                    "weight_qualifier": weight_qualifier,
                    "volume": volume,
                    "volume_qualifier": volume_qualifier,
                    "truck_type": truck_type,
                    "temperature": temperature,
                    "trucklength": trucklength,
                    "charges": charges,
                    "loading_quantity": loading_quantity
                })
                for k, v in shipment.items():
                    if v is None:
                        shipment.update({k: ""})

                general["Shipment Details"].append(shipment)

            # main_dict >> tables >> General Info >> Document References
            main_references = data.get("references")
            if main_references is None:
                ref = get_reference()
                general["Document References"].append(ref)

            elif len(main_references) == 0:
                ref = get_reference()
                general["Document References"].append(ref)

            else:
                for reference in main_references:
                    ref = get_reference()
                    id_ = reference.get("id")
                    idtype = reference.get("idtype")
                    if idtype not in ref_options:
                        idtype = "REFERENCE NUMBER"
                    _idtype = get_idtype(idtype)  # non-rendering
                    ref.update({
                        "id": id_,
                        "_idtype": _idtype,
                        "idtype": idtype  # non-rendering
                    })
                    for k, v in ref.items():
                        if v is None:
                            ref.update({k: ""})

                    general["Document References"].append(ref)

            # main_dict >> tables >> General Info >> Document Notes
            main_notes = data.get("notes")
            if main_notes is None:
                note = get_note()
                for k, v in note.items():
                    if v is None:
                        note.update({k: ""})

                general["Document Notes"].append(note)
            elif len(main_notes) == 0:
                note = get_note()
                for k, v in note.items():
                    if v is None:
                        note.update({k: ""})

                general["Document Notes"].append(note)
            else:
                for n in main_notes:
                    note = get_note()
                    # notetype = n.get("notetype")  # non-rendering
                    _notetype = n.get("_notetype")  # non-rendering
                    msg = n.get("note")
                    if msg is not None:
                        msg = re.sub(char_dict, "", msg)
                    else:
                        msg = ""

                    note.update({
                        "note": msg,
                        "notetype": "RATECON NOTES",  # non-rendering
                        "_notetype": "RN"  # non-rendering
                    })
                    for k, v in note.items():
                        if v is None:
                            note.update({k: ""})

                    general["Document Notes"].append(note)

            # main_schema >> Stops
            stops_data = data.get("stops")
            stop_count = 0
            if stops_data is None:
                stop1 = create_blank_stop("PICK", 1)
                stop2 = create_blank_stop("DROP", 2)
                main_dict["tables"]["Stops"].append(stop1)
                main_dict["tables"]["Stops"].append(stop2)
            elif len(stops_data) == 0:
                stop1 = create_blank_stop("PICK", 1)
                stop2 = create_blank_stop("DROP", 2)
                main_dict["tables"]["Stops"].append(stop1)
                main_dict["tables"]["Stops"].append(stop2)
            else:
                count = 1
                for stop in stops_data:
                    stops_dict = get_flat_stop_schema()
                    # Stop Type
                    stoptype_dict = get_stoptype()
                    stoptype = stop.get("stoptype")
                    _stoptype = stop.get("_stoptype")
                    ordinal = stop.get("ordinal")
                    if ordinal is None:
                        ordinal = count
                    if stoptype is not None:
                        stoptype_dict.update({
                            "stoptype": stoptype,
                            "_stoptype": _stoptype,  # non-rendering
                            "ordinal": ordinal
                        })
                    else:
                        print("[WARN] stoptype not found!")
                    stops_dict["Stop Type"].append(stoptype_dict)
                    # Dates
                    date_dict = get_date()
                    stop_dates = stop.get("dates")
                    if stop_dates is None:
                        for k, v in date_dict.items():
                            if v is None:
                                date_dict.update({k: ""})

                        stops_dict["Dates"].append(date_dict)
                        print(f"[WARN] No stop-level dates for stop number {stop_count}")
                    elif len(stop_dates) > 0:
                        if len(stop_dates) == 1:
                            date = stop_dates[0].get("date")
                            time = stop_dates[0].get("time")
                            datetype_0 = stop_dates[0].get("datetype")  # non-rendering
                            timetype_0 = stop_dates[0].get("timetype")  # non-rendering
                            date_dict.update({
                                "date_0": date,
                                "time_0": time,
                                "datetype_0": datetype_0,  # non-rendering
                                "timetype_0": timetype_0  # non-rendering
                            })
                            for k, v in date_dict.items():
                                if v is None:
                                    date_dict.update({k: ""})

                            stops_dict["Dates"].append(date_dict)
                        elif len(stop_dates) == 2:
                            date1 = stop_dates[0].get("date")
                            time1 = stop_dates[0].get("time")
                            datetype_0 = stop_dates[0].get("datetype")  # non-rendering
                            timetype_0 = stop_dates[0].get("timetype")  # non-rendering
                            date2 = stop_dates[1].get("date")
                            time2 = stop_dates[1].get("time")
                            datetype_1 = stop_dates[1].get("datetype")  # non-rendering
                            timetype_1 = stop_dates[1].get("timetype")  # non-rendering
                            date_dict.update({
                                "date_0": date1,
                                "time_0": time1,
                                "datetype_0": datetype_0,  # non-rendering
                                "timetype_0": timetype_0,  # non-rendering
                                "date_1": date2,
                                "time_1": time2,
                                "datetype_1": datetype_1,  # non-rendering
                                "timetype_1": timetype_1  # non-rendering
                            })
                            for k, v in date_dict.items():
                                if v is None:
                                    date_dict.update({k: ""})

                            stops_dict["Dates"].append(date_dict)
                    # Entity
                    entity_dict = get_entity()
                    entity = stop.get("entities")
                    if entity is not None:
                        if len(entity) == 0:
                            entity.append(get_entity())
                        contactname = ""
                        contact_number = ""
                        name = entity[0].get("name")
                        city = entity[0].get("city")
                        state = entity[0].get("state")
                        postal = entity[0].get("postal")
                        address = entity[0].get("address")
                        contacts = entity[0].get("contacts")
                        type_ = entity[0].get("type")
                        _type = entity[0].get("_type")
                        if contacts is not None:
                            contactname = contacts.get("contactname")
                            contact_number = contacts.get("contact_number")
                        entity_dict.update({
                            "type": type_,
                            "_type": _type,
                            "name": name,
                            "contactname": contactname,
                            "contact_number": contact_number,
                            "city": city,
                            "state": state,
                            "postal": postal
                        })
                        if isinstance(address, list):
                            if len(address) > 1:
                                entity_dict["address"] = []
                                for i in address:
                                    if isinstance(i, list):
                                        i = "".join(i)
                                    i = re.sub(char_dict, "", i)
                                    entity_dict["address"].append(i)
                            elif len(address) == 1:
                                entity_dict["address"] = []
                                if isinstance(address[0], list):
                                    address[0] = "".join(address[0])
                                ii = re.sub(char_dict, "", address[0])
                                entity_dict["address"].append(ii)
                        else:
                            print(f"[WARN] Extracted type of address is not list; address = {address}")
                        for k, v in entity_dict.items():
                            if isinstance(v, list):
                                if len(v) == 0:
                                    entity_dict.update({k: []})

                            elif v is None:
                                entity_dict.update({k: ""})

                        stops_dict["Entity"].append(entity_dict)
                    else:
                        for k, v in entity_dict.items():
                            if isinstance(v, list):
                                if len(v) == 0:
                                    entity_dict.update({k: [""]})

                            elif v is None:
                                entity_dict.update({k: ""})

                        stops_dict["Entity"].append(entity_dict)

                    # References
                    stop_references = stop.get("references")
                    if stop_references is None:
                        ref = get_reference()
                        for k, v in ref.items():
                            if v is None:
                                ref.update({k: ""})

                        stops_dict["References"].append(ref)
                    elif len(stop_references) == 0:
                        ref = get_reference()
                        for k, v in ref.items():
                            if v is None:
                                ref.update({k: ""})

                        stops_dict["References"].append(ref)
                    else:
                        for reference in stop_references:
                            ref = get_reference()
                            id_ = reference.get("id")
                            idtype = reference.get("idtype")
                            if idtype not in ref_options:
                                idtype = "REFERENCE NUMBER"
                            _idtype = get_idtype(idtype)  # non-rendering
                            ref.update({
                                "id": id_,
                                "_idtype": _idtype,
                                "idtype": idtype  # non-rendering
                            })
                            for k, v in ref.items():
                                if v is None:
                                    ref.update({k: ""})

                            stops_dict["References"].append(ref)

                    # Order Detail
                    stop_order_detail = stop.get("order_detail")
                    if len(stop_order_detail) == 0:
                        po = get_purchase_order()
                        for k, v in po.items():
                            if v is None:
                                po.update({k: ""})
                            else:
                                continue
                        stops_dict["Order Detail"].append(po)
                    else:
                        if len(stop_order_detail) > 0:
                            for p in stop_order_detail:
                                po = get_purchase_order()
                                po_number = p.get("purchase_order_number")
                                date = p.get("date")
                                cases = p.get("cases")
                                weight_unit_code = p.get("weight_unit_code")
                                weight = p.get("weight")
                                volume_type = p.get("volume_type")
                                volume_units = p.get("volume_units")
                                po.update({
                                    "purchase_order_number": po_number,
                                    "date": date,
                                    "cases": cases,
                                    "weight": weight,
                                    "weight_unit_code": weight_unit_code,
                                    "volume_type": volume_type,
                                    "volume_units": volume_units
                                })
                                for k, v in po.items():
                                    if v is None:
                                        po.update({k: ""})

                                stops_dict["Order Detail"].append(po)

                    # Notes
                    stop_notes = stop.get("notes")
                    if stop_notes is None:
                        note = get_note()
                        for k, v in note.items():
                            if v is None:
                                note.update({k: ""})

                        stops_dict["Notes"].append(note)
                    elif len(stop_notes) == 0:
                        note = get_note()
                        for k, v in note.items():
                            if v is None:
                                note.update({k: ""})

                        stops_dict["Notes"].append(note)
                    else:
                        for n in stop_notes:
                            note = get_note()
                            if n is None:
                                stops_dict["Notes"].append(note)
                            else:
                                msg = n.get("note")
                                notetype = n.get("notetype")  # non-rendering
                                _notetype = n.get("_notetype")  # non-rendering
                                if msg is not None:
                                    msg = re.sub(char_dict, "", msg)
                                else:
                                    msg = ""

                                note.update({
                                    "note": msg,
                                    "notetype": notetype,  # non-rendering
                                    "_notetype": _notetype  # non-rendering
                                })
                                for k, v in note.items():
                                    if v is None:
                                        note.update({k: ""})

                                stops_dict["Notes"].append(note)
                        count += 1
                    main_dict["tables"]["Stops"].append(stops_dict)
            # Now, to make sure that there are no illegal characters present in our new JSON dict
            # to prevent the frontend from crashing.
            try:
                flattened_data = json.loads(
                    json.dumps(main_dict, indent=2, cls=DecimalEncoder, separators=(',', ': ')))
                ddb_copy["autoextracts"]["data"] = flattened_data
                print(f"[FLATTENED DOC] = {json.dumps(flattened_data)}")
                return True, ddb_copy, ""
            except Exception as je:
                print(f"[DEBUG] json.loads(json.dumps()) could not parse with cls; ERROR = {je}")
                try:
                    flattened_data = json.loads(
                        json.dumps(main_dict, indent=2, separators=(',', ': ')))
                    ddb_copy["autoextracts"]["data"] = flattened_data
                    print(f"[FLATTENED DOC] = {json.dumps(flattened_data)}")
                    return True, ddb_copy, f"{je}"
                except Exception as jeee:
                    print(f"[DEBUG] json.loads(json.dumps()) could not parse data; ERROR = {jeee}")
                    print("[FAIL] Dictionary contains characters that are illegal JSON syntax; Defaulting to blank schema")
                    ddb_copy["autoextracts"]["data"] = fail_schema()
                    return True, ddb_copy, f"{jeee}"

    except Exception as e:
        print(f"[ERROR] {func} failed; Error ==> {e}")
        traceback.print_exc()
        try:
            ddb_obj["autoextracts"]["data"] = fail_schema()
            return False, ddb_obj, f"{e}"
        except Exception as ee:
            print(f"[DOUBLE FAIL] failed to generate blank schema to return; ERROR = {ee}")
            traceback.print_exc()
            return False, {}, f"{ee}"


#  BLANK main DICTIONARY:
def get_rate_confirmation_schema():
    rate_confirmation_schema = {
        "transaction_type": "204",
        "sender": None,  # BROKER or SHIPPER if they are not having a broker. Example: "Werner Logistics"
        "receiver": {
            "name": None,  # carrier-name on top right of page
            "isa_qual": "ZZ",  # hard-coded
            "isa_ID": None  # client email
        },
        "client": None,  # hard-coded. Example: "Werner Logistics"
        "submitted_time": None,  # time we received the email
        "identifier": None,
        "identifier_type": None,
        "shipment": {
            "equipment_number": None,
            "distance": None,
            "weight": None,
            "weight_unit_code": None,
            "weight_qualifier": "GROSS WEIGHT",  # hard-coded
            "volume": None,
            "volume_qualifier": None,
            "truck_type": None,
            "temperature": None,
            "trucklength": None,
            "charges": None,
            "loading_quantity": None
        },
        "purpose": "ORIGINAL",
        "references": [],  # append references_schema here for reference numbers ABOVE Shipper/Consignee
        "dates": [],  # append dates_schema here if any, don't include stop dates
        "notes": [],  # append notes_schema here for notes/comments ABOVE Shipper/Consignee
        "entities": [],  # append entities_schema here
        "stops": [],  # append stops_schema here

    }
    return rate_confirmation_schema


# BLANK references DICTIONARY:
# used for rate-con level references as well as stop-level references
def get_reference_schema():
    reference_schema = {
        "id": None,
        "idtype": None,
        "_idtype": None
    }
    return reference_schema


# BLANK dates DICTIONARY:
def get_dates_schema():
    dates_schema = {
        "date": None,  # dd/mm/yyyy hh:mm
        "datetype": None,  # always "RESPOND BY", "EP", or "LP"?None
        "time": None,
        "timetype": None
        # always "MUST RESPOND BY", "EARLIEST REQUESTED (PICKUP|DROP) TIME", "LATEST REQUESTED (PICKUP|DROP) TIME"?
    }
    return dates_schema


# BLANK references DICTIONARY:
# used for rate-con level notes as well as stop-level notes
def get_note_schema():
    note_schema = {
        "note": None,
        "notetype": None,
        "_notetype": None
    }
    return note_schema


# BLANK entites DICTIONARY VARIABLE:
#  can be Broker, Shipper, or Consignee
def get_entity_schema(entity_type):
    entity_schema = {
        "name": None,
        "type": None,
        "_type": None,
        "id": "",
        "idtype": "MUTUALLY DEFINED",  # hard-coded
        "_idtype": "ZZ",  # hard-coded
        "address": [],  # List object ['address part 1', 'address part 2']
        "city": None,
        "state": None,
        "postal": None,
        "country": None,
        "contacts": {
            "contactname": None,
            "contact_type": None,
            "contact_number": None,
            "contact_number_type": None
        }
    }

    if entity_type.upper() == "SHIPPER":
        entity_schema['type'] = "SHIPPER"
        entity_schema['_type'] = "SH"
        return entity_schema
    elif entity_type.upper() == "CONSIGNEE":
        entity_schema['type'] = "CONSIGNEE"
        entity_schema['_type'] = "CN"
        return entity_schema
    elif entity_type.upper() == "BROKER":
        entity_schema['type'] = "BROKER"
        entity_schema['_type'] = "BK"
        return entity_schema
    else:
        print("Select correct entity type (SHIPPER/CONSIGNEE/BROKER)")
    return entity_schema


# BLANK purchase_order DICTIONARY to be appended to "order_detail" in stops dictionary IF:

# -- if only ONE PO, fill out "stops"["order_detail"] and ignore this extra dictionary.
# -- if multiple PO's use this dictionary and append to "order_detail"["purchase_order_number"] in stops dictionary.
def get_purchase_order_schema():
    purchase_order_schema = {
        "purchase_order_number": None,
        "date": None,
        "cases": None,  # quantity
        "weight_unit_code": None,  # "L" for pounds, "K" for Kilo
        "weight": None,
        "volume_type": None,  # "cubic feet", etc
        "volume_units": None
    }
    return purchase_order_schema


# BLANK stops DICTIONARY:

#  _stopType Codes for Picks & Drops:
#  Picks:
#  LD (Load)   <--- Duke to use this one in general
#  PL (Partial Load)
#  CL (Complete Load)
#  RT (Retrieval of Trailer)

#  Drops:
#  UL (Unload)  <-- Duke to use this one in general
#  PU (Partial Unload)
#  CU (Complete Unload)
#  DT (Drop Trailer)

def get_stops_schema(stop_type, ordinal: int):
    stop_schema = {
        "stoptype": None,  # see stoptype codes for pickups and drops
        "_stoptype": None,  # see stoptype codes for pickups and drops
        "ordinal": ordinal,  # starts from 1 for first "PICK"
        "dates": [],  # append dates_schema here
        "references": [],  # append references_schema here for stop references
        "order_detail": [],
        "entities": [],  # append entities_schema here for stop-level entities
        "notes": []  # append notes_schema here for stop-level notes/comments
    }

    if stop_type.upper() == "PICK":
        stop_schema['stoptype'] = "PICK"
        stop_schema['_stoptype'] = "LD"
        return stop_schema
    elif stop_type.upper() == "DROP":
        stop_schema['stoptype'] = "DROP"
        stop_schema['_stoptype'] = "UL"
        return stop_schema
    else:
        print("Select correct entity type (PICK/DROP)")
    return stop_schema


def unflatten_ratecon_time(time_str):
    func = unflatten_ratecon_time.__name__
    try:
        if time_str is None:
            return True, None, ""

        elif not bool(re.compile(r"\S").search(time_str)):
            print(f"Time is empty string, skipping...")
            return True, None, ""

        else:

            try:
                time_ = datetime.datetime.strptime(time_str, '%H:%M')
                time_0 = time_.strftime('%H:%M')
            except Exception as te:
                print(f"[{func}] Warning ==> {te}")

                try:
                    time_ = datetime.datetime.strptime(time_str, '%H:%M:%S')
                    time_0 = time_.strftime('%H:%M')
                except Exception as te2:
                    print(f"[{func}] Warning ==> {te2}")

                    try:
                        time_ = datetime.datetime.strptime(time_str, '%H:%M:%S.%f')
                        time_0 = time_.strftime('%H:%M')
                    except Exception as te3:
                        print(f"[ERROR PARSING TIME] submitted time: {time_str} ==> {te3}")
                        raise Exception(f"Time ({time_str}) is incorrect format >>> {te3}")

            return True, time_0, ""
    except Exception as e:
        print(f"[ERROR] {func} Error ==> {e}")
        traceback.print_exc()
        return False, None, f"{e}"


def unflatten_ratecon_date(date_str):
    func = unflatten_ratecon_date.__name__
    try:
        if date_str is None:
            return True, None, ""

        elif not bool(re.compile(r"\S").search(date_str)):
            print(f"Date is empty string, skipping...")
            return True, None, ""

        elif date_str.lower() in ["n/a", "na"]:
            return True, None, ""

        else:
            try:
                date_ = datetime.datetime.strptime(date_str, '%Y-%m-%d')
                date_0 = date_.strftime('%Y-%m-%d')
            except Exception as de:
                raise Exception(f"Date submitted ({date_str}) is incorrectly formatted. Should be YYYY-mm-dd; Error ==> {de}")

            return True, date_0, ""
    except Exception as e:
        print(f"[ERROR] {func} Error ==> {e}")
        traceback.print_exc()
        return False, None, f"{e}"


def unflatten_rate_confirmation(flattened_ddb_entry: str) -> tuple[bool, dict, str]:
    """
    Takes flattened data from the Dynamotator UI and rebuilds the information into the original Ratecon Schema;
    :param flattened_ddb_entry: JSON str
    :return: JSON str, Original ratecon schema inside the ddb_entry.
    """
    func = unflatten_rate_confirmation.__name__
    if isinstance(flattened_ddb_entry, dict):
        flattened_ddb_entry = json.dumps(flattened_ddb_entry)

    data = json.loads(flattened_ddb_entry)
    main = get_rate_confirmation_schema()
    try:
        general = data["headers"]["General"]
        identifier = general.get("identifier")
        identifier_type = general.get("identifier_type")
        client = general.get("client")
        sender = general.get("sender")
        receiver = general.get("receiver")
        isa_id = general.get("isa_ID")
        main.update({
            "client": client,
            "sender": sender,
            "identifier": identifier,
            "identifier_type": identifier_type
        })
        main["receiver"].update({
            "name": receiver,
            "isa_ID": isa_id
        })

        ship = data["tables"]["General Info"][0]["Shipment Details"][0]
        distance = ship.get("distance")
        equipment_number = ship.get("equipment_number")
        weight = ship.get("weight")
        weight_unit_code = ship.get("weight_unit_code")
        weight_qualifier = ship.get("weight_qualifier")
        volume = ship.get("volume")
        volume_qualifier = ship.get("volume_qualifier")
        truck_type = ship.get("truck_type")
        temperature = ship.get("temperature")
        trucklength = ship.get("trucklength")
        charges = ship.get("charges")
        if charges is not None:
            if charges.lower() in ["na", "n/a"]:
                charges = "0.00"
            else:
                charges = re.sub(r"[^\d.,]+", "", charges)
        loading_quantity = ship.get("loading_quantity")
        main["shipment"].update({
            "distance": distance,
            "equipment_number": equipment_number,
            "weight": str(weight),
            "weight_unit_code": weight_unit_code,
            "weight_qualifier": weight_qualifier,
            "volume": volume,
            "volume_qualifier": volume_qualifier,
            "truck_type": truck_type,
            "temperature": temperature,
            "trucklength": trucklength,
            "charges": charges,
            "loading_quantity": loading_quantity
        })
        for k, v in main['shipment'].items():
            if v is None or not bool(re.compile(r"\S").search(str(v))):
                main['shipment'].update({k: None})

        flt_dates = data["tables"]["General Info"][0]["Document Dates"]
        date_dict_0 = get_dates_schema()
        for i in flt_dates:

            date_success, date_0, date_err = unflatten_ratecon_date(date_str=i.get('date_0'))
            if not date_success:
                raise Exception(f"unflatten_ratecon_date() >>> {date_err}")

            time_success, time_0, time_err = unflatten_ratecon_time(time_str=i.get('time_0'))
            if not time_success:
                raise Exception(f"unflatten_ratecon_time() >>> {time_err}")

            datetype_0 = i.get("datetype_0")
            timetype_0 = i.get("timetype_0")
            date_dict_0.update({
                "date": date_0,
                "datetype": datetype_0,
                "time": time_0,
                "timetype": timetype_0
            })
            for k, v in date_dict_0.items():
                if v is None or not bool(re.compile(r"\S").search(str(v))):
                    date_dict_0.update({k: None})

            if re.compile(r"\d").search(str(date_dict_0["date"])) or re.compile(r"\d").search(str(date_dict_0["time"])):
                main["dates"].append(date_dict_0)
            else:
                print(f"[INFO] Passing over date in Document Dates, no values found")
                main["dates"] = []

        flt_note = data["tables"]["General Info"][0]["Document Notes"]
        if isinstance(flt_note, list):
            if len(flt_note) == 0:
                print("[INFO] No Document-level notes found")
                main["notes"] = []
            else:
                for i in flt_note:
                    note = dict(get_note_schema())
                    msg = i.get("note")
                    note.update({
                        "note": msg,
                        "notetype": "RATECON NOTES",
                        "_notetype": "RN"
                    })
                    if note['note'] is not None:
                        if re.compile(r"[a-zA-Z0-9]").search(note["note"]):
                            main["notes"].append(note)
                        else:
                            print(f"[INFO] No Document-level notes found")
                            continue
                    else:
                        print(f"[INFO] No Document-level notes found")
                        continue
        else:
            print("[WARN] Incoming type of notes from tables>>Document Notes does not match expected datatype of list")
            main["notes"] = []

        broker_dict = get_entity_schema("BROKER")
        flt_broker = data["headers"]["Broker Details"]
        name_ = "None"
        city_ = "None"
        state_ = "None"
        postal_ = "None"
        flt_address = flt_broker.get("address")
        name = flt_broker.get("name")
        if name is not None:
            name = name.upper()
            name_ = name
        city = flt_broker.get("city")
        if city is not None:
            city = city.upper()
            city_ = city
        state = flt_broker.get("state")
        if state is not None:
            if isinstance(state, str):
                for name, abbrev in STATES.items():
                    if state.lower() == name.lower():
                        print(f"[STATE ABBREV CONVERSION] state={state}; converted to: {abbrev.upper()}")
                        state = abbrev.upper()
                    elif state.lower() == abbrev.lower():
                        print(f"[STATE ABBREV MATCHED] state={state.upper()}")
                        state = abbrev.upper()

        postal = flt_broker.get("postal")
        if postal is not None:
            postal_ = postal
        uid_ = name_ + city_ + state + postal_
        uid = re.sub('[^A-Za-z0-9]+', '', uid_)
        contactname = flt_broker.get("contactname")
        contact_type = flt_broker.get("contact_type")
        contact_number = flt_broker.get("contact_number")
        contact_number_type = flt_broker.get("contact_number_type")
        broker_dict.update({
            "id": uid,
            "name": name,
            "city": city,
            "state": state,
            "postal": postal,
            "country": "USA"
        })
        if len(flt_address) == 0:
            print("[INFO] no broker address found!")
            broker_dict["address"] = []
        elif isinstance(flt_address, list):
            if len(flt_address) == 1:
                if isinstance(flt_address[0], list):
                    flt_address[0] = "".join(flt_address[0])
                broker_dict["address"].append(flt_address[0])
            elif len(flt_address) >= 2:
                for i in flt_address:
                    if isinstance(i, list):
                        i = "".join(i)
                    broker_dict["address"].append(i)
        elif isinstance(flt_address, str):
            if len(flt_address) >= 1:
                add_lst = [flt_address]
                broker_dict["address"] = add_lst
            else:
                broker_dict["address"] = []

        broker_dict["contacts"].update({
            "contactname": contactname,
            "contact_type": contact_type,
            "contact_number": contact_number,
            "contact_number_type": contact_number_type
        })
        main["entities"].append(broker_dict)

        flt_references = data["tables"]["General Info"][0]["Document References"]
        if isinstance(flt_references, list):
            if len(flt_references) == 0:
                print("[INFO] No Document-level references found")
                main["references"] = []
            else:
                for i in flt_references:
                    if i.get('id') is None:
                        print(f"skipping NonType reference...")
                        continue
                    if not bool(re.compile(r"\S").search(i.get('id'))):
                        print(f"skipping empty reference...")
                        continue
                    ref = get_reference_schema()
                    _id = i.get("id")
                    idtype = i.get("idtype")
                    _idtype = get_idtype(idtype)
                    ref.update({
                        "id": _id,
                        "_idtype": _idtype,
                        "idtype": idtype
                    })

                    if re.compile(r"[a-zA-Z0-9]").search(str(ref['id'])):
                        main["references"].append(ref)
                    else:
                        main["references"] = []
        else:
            print("[WARN] Incoming type of references from tables>>Document References does not match expected datatype of list")
            main["references"] = []

        flt_stops = data["tables"]["Stops"]
        ordinal = 1
        for s in flt_stops:
            _type = s.get("Stop Type")
            stoptype = _type[0].get("stoptype")
            if stoptype is None or (isinstance(stoptype, str) and stoptype.lower() in ["na", "n/a"]):
                raise Exception(f"Stoptype in stop {ordinal} is blank!")

            stop_dict = get_stops_schema(stoptype, ordinal)

            dates = s["Dates"]
            if len(dates) == 0:
                print(f"[INFO] Passing over primary date in stop {str(ordinal)}, no values found")
                stop_dict["dates"] = []

            elif len(dates) == 1:
                date_dict_0 = dict(get_dates_schema())
                dates = dates[0]

                s_date_success, date_0, s_date_err = unflatten_ratecon_date(date_str=dates.get("date_0"))
                if not s_date_success:
                    raise Exception(f"[Stop {ordinal} - Date 1] unflatten_ratecon_date() >>> {s_date_err}")

                s_time_success, time_0, s_time_err = unflatten_ratecon_time(time_str=dates.get("time_0"))
                if not s_date_success:
                    raise Exception(f"[Stop {ordinal} - Time 1] unflatten_ratecon_time() >>> {s_time_err}")

                datetype_0 = dates.get("datetype_0")
                timetype_0 = dates.get("timetype_0")
                date_dict_0.update({
                    "date": date_0,
                    "datetype": datetype_0,
                    "time": time_0,
                    "timetype": timetype_0
                })
                for k, v in date_dict_0.items():
                    if v is None or not bool(re.compile(r"\S").search(str(v))):
                        date_dict_0.update({k: None})

                if re.compile(r"\d").search(str(date_dict_0["date"])) or re.compile(r"\d").search(str(date_dict_0["time"])):
                    stop_dict["dates"].append(date_dict_0)
                else:
                    stop_dict["dates"] = []

            elif len(dates) >= 2:
                for d in dates:
                    date_dict_1 = dict(get_dates_schema())
                    date_idx = dates.index(d)

                    s_date_success, date_1, s_date_err = unflatten_ratecon_date(date_str=d.get("date_0"))
                    if not s_date_success:
                        raise Exception(f"[Stop {ordinal} - Date {date_idx + 1}] unflatten_ratecon_date() >>> {s_date_err}")

                    s_time_success, time_1, s_time_err = unflatten_ratecon_time(time_str=d.get("time_0"))
                    if not s_date_success:
                        raise Exception(f"[Stop {ordinal} - Time {date_idx + 1}] unflatten_ratecon_time() >>> {s_time_err}")

                    datetype_1 = d.get("datetype_0")
                    timetype_1 = d.get("timetype_0")
                    date_dict_1.update({
                        "date": date_1,
                        "datetype": datetype_1,
                        "time": time_1,
                        "timetype": timetype_1
                    })
                    for k, v in date_dict_1.items():
                        if v is None or not bool(re.compile(r"\S").search(str(v))):
                            date_dict_1.update({k: None})

                    if re.compile(r"\d").search(str(date_dict_1["date"])) or re.compile(r"\d").search(str(date_dict_1["time"])):
                        stop_dict["dates"].append(date_dict_1)
                    else:
                        print(f"[INFO] Passing over date in stop {str(ordinal)}, no values found")
                        continue

            references = s.get("References")
            if isinstance(references, list):
                if len(references) == 0:
                    print(f"[INFO] No Stop-level references found in stop numer {str(ordinal)}")
                    stop_dict["references"] = []
                else:
                    for r in references:
                        if r.get('id') is None:
                            print(f"skipping NonType reference...")
                            continue
                        if not bool(re.compile(r"\S").search(r.get('id'))):
                            print(f"skipping empty reference...")
                            continue
                        ref = dict(get_reference_schema())
                        _id = r.get("id")
                        idtype = r.get("idtype")
                        _idtype = get_idtype(idtype)
                        ref.update({
                            "id": _id,
                            "_idtype": _idtype,
                            "idtype": idtype
                        })

                        if re.compile(r"[a-zA-Z0-9]").search(str(ref['id'])):
                            stop_dict["references"].append(ref)
                        else:
                            continue
            else:
                print(
                    f"[WARN] Incoming type of references from stop number {str(ordinal)} does not match expected datatype of list")
                stop_dict["references"] = []

            flt_notes = s.get("Notes")
            if isinstance(flt_notes, list):
                if len(flt_notes) == 0:
                    print(f"[INFO] No Stop-level notes found in stop number {str(ordinal)}")
                    stop_dict["notes"] = []
                else:
                    for n in flt_notes:
                        note = dict(get_note_schema())
                        msg = n.get("note")
                        note.update({
                            "note": msg,
                            "notetype": "STOP NOTES",
                            "_notetype": "SN"
                        })

                        if note['note'] is not None:
                            if re.compile(r"[a-zA-Z0-9]").search(str(note['note'])):
                                stop_dict["notes"].append(note)
                            else:
                                print(f"[INFO] No note found in stop number {str(ordinal)}")
                                continue
                        else:
                            print(f"[INFO] No note found in stop number {str(ordinal)}")
                            continue
            else:
                print(
                    f"[WARN] Incoming type of notes from stop number {str(ordinal)} does not match expected datatype of list")

            flt_po = s["Order Detail"]
            if isinstance(flt_po, list):
                if len(flt_po) == 0:
                    print(f"[INFO] No Order Detail(s) found in stop number {str(ordinal)}")
                    stop_dict["order_detail"] = [get_purchase_order_schema()]
                else:
                    for p in flt_po:
                        po = get_purchase_order_schema()
                        po_num = p.get("purchase_order_number")
                        date = p.get("date")
                        cases = p.get("cases")
                        weight = p.get("weight")
                        weight_unit_code = p.get("weight_unit_code")
                        volume_type = p.get("volume_type")
                        volume_units = p.get("volume_units")
                        po.update({
                            "purchase_order_number": po_num,
                            "date": date,
                            "cases": cases,
                            "weight": weight,
                            "weight_unit_code": weight_unit_code,
                            "volume_type": volume_type,
                            "volume_units": volume_units
                        })
                        stop_dict["order_detail"].append(po)

            else:
                print(f"[WARN] Incoming type of Order Detail from stop number {str(ordinal)} does not match expected datatype of list")
                stop_dict["order_detail"] = []

            ent = s["Entity"][0]
            _type = ent.get("type")
            if _type is None:
                _type2 = s.get("Stop Type")
                stoptype = _type2[0].get("stoptype")
                if stoptype.lower() == "pick":
                    _type = "SHIPPER"
                elif stoptype.lower() == "drop":
                    _type = "CONSIGNEE"
                elif _type is None:
                    raise Exception("stoptype is not one of [pick, drop]")

            entity = get_entity_schema(_type)
            name_ = "None"
            city_ = "None"
            state_ = "None"
            postal_ = "None"
            flt_address = []
            if ent.get("address") is not None:
                flt_address.append(ent.get("address"))
            name = ent.get("name")
            if name is not None:
                name = name.upper()
                name_ = name
            city = ent.get("city")
            if city is not None:
                city = city.upper()
                city_ = city

            state = ent.get("state")
            if state is not None:
                if isinstance(state, str):
                    for st, abbrev in STATES.items():
                        if state.lower() == st.lower():
                            print(f"[STATE ABBREV CONVERSION] state={state}; converted to: {abbrev.upper()}")
                            state = abbrev.upper()
                        elif state.lower() == abbrev.lower():
                            print(f"[STATE ABBREV MATCHED] state={state.upper()}")
                            state = abbrev.upper()

            postal = ent.get("postal")
            if postal is not None:
                postal_ = postal


            uid_ = name_ + city_ + state + postal_
            uid = re.sub('[^A-Za-z0-9]+', '', uid_)
            contactname = ent.get("contactname")
            contact_number = ent.get("contact_number")
            contact_type = ent.get("contact_type")
            contact_number_type = ent.get("contact_number_type")
            entity.update({
                "id": uid,
                "name": name,
                "city": city,
                "state": state,
                "postal": postal,
                "country": "USA"
            })

            if isinstance(flt_address, list):
                if len(flt_address) == 0:
                    print("[INFO] no entity address found!")
                    entity["address"] = []
                elif len(flt_address) >= 1:
                    for i in flt_address:
                        if isinstance(i, list):
                            i = "".join(i)
                        entity["address"].append(i)
            elif isinstance(flt_address, str):
                if len(flt_address) >= 1:
                    add_lst = [flt_address]
                    entity["address"] = add_lst
                else:
                    entity['address'] = 0

            entity["contacts"].update({
                "contactname": contactname,
                "contact_type": contact_type,
                "contact_number": contact_number,
                "contact_number_type": contact_number_type
            })

            stop_dict["entities"].append(entity)
            main["entities"].append(entity)
            main["stops"].append(stop_dict)
            ordinal += 1

        print(f"TRANSLATED DOCUMENT = {json.dumps(main)}")
        return True, main, ""

    except Exception as e:
        print(f"[ERROR] {func} Error ==> {e}")
        traceback.print_exc()
        return False, {}, f"{e}"

