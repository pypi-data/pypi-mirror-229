import traceback
import datetime
import re


REFERENCE_OPTIONS = {
            "ACCOUNT NUMBER": "4F",
            "APPOINTMENT NUMBER": "AO",
            "BILL OF LADING": "BM",
            "BOOKING NUMBER": "BN",
            "CARRIER REFERENCE": "CR",
            "CHASSIS NUMBER": "KL",
            "CONSIGNEE'S ORDER NUMBER": "CG",
            "CONTAINER NUMBER": "OC",
            "CONTRACT REFERENCE NUMBER": "KL",
            "CUSTOMER'S ORDER NUMBER": "CO",
            "CUSTOMER'S REFERENCE NUMBER": "CR",
            "DELIVERY ORDER NUMBER": "DO",
            "DELIVERY REFERENCE": "KK",
            "DISPATCH PHONE NUMBER": "42",
            "DRIVER PHONE NUMBER": "42",
            "EQUIPMENT NUMBER": "EQ",
            "ID NUMBER": "KL",
            "LOAD PLANNING NUMBER": "LO",
            "MANIFEST NUMBER": "Y5",
            "MC NUMBER": "MCI",
            "MUTUALLY DEFINED": "ZZ",
            "PICKUP APPOINTMENT NUMBER": "PUA",
            "PICKUP REFERENCE NUMBER": "P8",
            "PURCHASE ORDER NUMBER": "PO",
            "RATE CODE NUMBER": "RB",
            "REFERENCE NUMBER": "KL",
            "SALES ALLOWANCE NUMBER": "OT",
            "SERVICE CHARGE NUMBER": "SV",
            "SHIPMENT DESTINATION CODE": "4C",
            "SHIPMENT ORIGIN CODE": "4B",
            "SHIPPER'S IDENTIFYING NUMBER": "SI",
            "SHIPPER'S ORDER NUMBER": "SO",
            "SUBCONTRACT NUMBER": "3X",
            "TRANSACTION REFERENCE NUMBER": "TN",
            "VESSEL NUMBER": "WU"
        }


def get_idtype(_idtype):
    """
    Pass in the id type description to get the id type code.
    """
    func = get_idtype.__name__
    try:
        _idtype = _idtype.upper()
        for k, v in REFERENCE_OPTIONS.items():
            if k == _idtype:
                return v

        raise Exception(f"Failed to find match for {_idtype}")
    except Exception as e:
        print(f"[WARN] {func} Error ==> {e}")
        traceback.print_exc()
        return "KL"


STATES = {
    'alabama': 'al',
    'alaska': 'ak',
    'arizona': 'az',
    'arkansas': 'ar',
    'california': 'ca',
    'colorado': 'co',
    'connecticut': 'ct',
    'delaware': 'de',
    'florida': 'fl',
    'georgia': 'ga',
    'hawaii': 'hi',
    'idaho': 'id',
    'illinois': 'il',
    'indiana': 'in',
    'iowa': 'ia',
    'kansas': 'ks',
    'kentucky': 'ky',
    'louisiana': 'la',
    'maine': 'me',
    'maryland': 'md',
    'massachusetts': 'ma',
    'michigan': 'mi',
    'minnesota': 'mn',
    'mississippi': 'ms',
    'missouri': 'mo',
    'montana': 'mt',
    'nebraska': 'ne',
    'nevada': 'nv',
    'new hampshire': 'nh',
    'new jersey': 'nj',
    'new mexico': 'nm',
    'new york': 'ny',
    'north carolina': 'nc',
    'north dakota': 'nd',
    'ohio': 'oh',
    'oklahoma': 'ok',
    'oregon': 'or',
    'pennsylvania': 'pa',
    'rhode island': 'ri',
    'south carolina': 'sc',
    'south dakota': 'sd',
    'tennessee': 'tn',
    'texas': 'tx',
    'utah': 'ut',
    'vermont': 'vt',
    'virginia': 'va',
    'washington': 'wa',
    'west Virginia': 'wv',
    'wisconsin': 'wi',
    'wyoming': 'wy',
    'district of columbia': 'dc'
}


def format_state(state: str, abbreviate: bool):
    """
    Checks and normalizes a US state name according to the <abbreviate> parameter.
    :param state: str,;
    :param abbreviate: bool
    """
    func = format_state.__name__
    try:
        found = False
        state = re.sub(r" \B", "", state.lower())  # remove trailing end space
        state = re.sub(r"\B ", "", state.lower())  # remove trailing start space
        state = re.sub(r" +", " ", state.lower())  # remove extra spaces
        val = None
        for s, abbrev in STATES.items():
            if s == state:
                found = True
                if abbreviate:
                    val = abbrev.upper()
                    break
                else:
                    val = s.title()
                    break

            elif abbrev == state:
                found = True
                if abbreviate:
                    val = abbrev.upper()
                    break
                else:
                    val = s.title()
                    break

        if not found:
            raise Exception(f"State ({state}) is not valid")

        return found, val, f"Abbreviated: {abbreviate}"
    except Exception as e:
        print(f"[ERROR] {func} Error ==> {e}")
        traceback.print_exc()
        return False, None, f"{e}"


def parse_incoming_address(address):
    """
    Parses an incoming address from the DT to a normalized string;
    Accepts: strings, list of strings, list-of-list of strings
    :param address: <who knows>, incoming address from the DT;
    :return: bool(success), str(address), str(error).
    """
    func = parse_incoming_address.__name__
    try:
        if isinstance(address, list):
            if len(address) == 0:
                return True, "", ""
            if len(address) == 1:
                address = address[0]
                if isinstance(address, str):
                    address = address.title()
                elif isinstance(address, list):
                    if len(address) == 1:
                        address = address[0].title()
                    else:
                        address = [a.title() for a in address]
                        address = ", ".join(address)
            else:
                if isinstance(address[0], str):
                    address = [a.title() for a in address]
                    address = ", ".join(address)
                else:
                    address_ = list()
                    for a_list in address:
                        if isinstance(a_list[0], str):
                            address_.extend([a.title() for a in a_list])
                    address = ", ".join(address_)

        print(f"[{func}] DataType: {type(address)}; Value: {address}")

        return True, address, ""
    except Exception as e:
        print(f"[ERROR] {func} ==> {e}")
        traceback.print_exc()
        return False, None, f"{e}"


def parse_time(time_str):
    func = parse_time.__name__
    try:
        try:
            time_ = datetime.datetime.strptime(time_str, '%I:%M %p')
            time_str = time_.strftime('%H:%M')
        except ValueError as TimeError1:
            print(f"[WARN] TimeError1 ==> {TimeError1}")
            try:
                time_ = datetime.datetime.strptime(time_str, '%I:%M%p')
                time_str = time_.strftime('%H:%M')
            except ValueError as TimeError2:
                print(f"[WARN] TimeError2 ==> {TimeError2}")
                try:
                    time_ = datetime.datetime.strptime(time_str, '%H:%M:%S.%f')
                    time_str = time_.strftime('%H:%M')
                except ValueError as TimeError3:
                    print(f"[WARN] TimeError3 ==> {TimeError3}")
                    try:
                        time_ = datetime.datetime.strptime(time_str, '%H:%M:%S')
                        time_str = time_.strftime('%H:%M')
                    except ValueError as TimeError4:
                        print(f"[WARN] TimeError4 ==> {TimeError4}")
                        try:
                            time_ = datetime.datetime.strptime(time_str, '%H:%M')
                            time_str = time_.strftime('%H:%M')
                        except ValueError as TimeError5:
                            print(f"[WARN] TimeError5 ==> {TimeError5}")
                            raise Exception(f"No time-patterns matched: {time_str}")

        return True, time_str, ""
    except Exception as e:
        print(f"[ERROR] {func} Error ==> {e}")
        traceback.print_exc()
        return False, None, f"{e}"


def format_time(time):
    func = format_time.__name__
    try:
        try:
            time_ = datetime.datetime.strptime(time, '%I:%M %p')
        except Exception as ee:
            print(f"[{func} Warning] {ee}")
            time_ = datetime.datetime.strptime(time, '%H:%M')

        return True, time_, ""

    except Exception as e:
        print(f"[ERROR] {func} Error ==> {e}")
        traceback.print_exc()
        return False, None, f"{e}"
