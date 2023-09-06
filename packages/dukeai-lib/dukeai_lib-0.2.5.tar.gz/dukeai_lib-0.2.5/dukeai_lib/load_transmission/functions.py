import boto3
import traceback
from dukeai_lib.tools import gen_random_sha


def get_or_create_vendor(req_id: str, sender: str, client_obj: dict, invoice_table):
    """
    Gets or Creates a Vendor object for a DUKE user during a load transmission;
    :param req_id: str;
    :param sender: str;
    :param client_obj: dict;
    :param invoice_table: boto3.resources.factory.dynamodb.Table;
    :return:
    """
    func = get_or_create_vendor.__name__
    try:
        vendor_email = client_obj['bill_to_email'].upper()
        vendor_info_q = invoice_table.get_item(Key={'cust_id': sender, 'vendor_email': vendor_email})
        vendor_info = vendor_info_q.get('Item')
        if vendor_info is not None:
            return True, vendor_info, ""

        else:
            # If vendor object does not exist, then create it
            recipient_vendor_info = {
                'vendor_email': client_obj.get('bill_to_email'),
                'company_name': client_obj.get('company_name'),
                'address': client_obj['company_info'].get('street1'),
                'address2': client_obj['company_info'].get('street2'),
                'phone': client_obj['company_info'].get('phone'),
                'contact': client_obj['company_info'].get('contact'),
                'city': client_obj['company_info'].get('city'),
                'state': client_obj['company_info'].get('state'),
                'postal': client_obj['company_info'].get('postal'),
                'country': 'USA'
            }
            create_vendor_success, vendor_info, create_vendor_err = create_vendor_from_recipient(
                cust_id=sender,
                vendor_info=recipient_vendor_info,
                invoice_table=invoice_table
            )
            if not create_vendor_success:
                raise Exception(f"create_vendor_from_recipient() >>> {create_vendor_err}")

            return True, vendor_info, ""

    except Exception as e:
        print(f"[({req_id}) ERROR] {func} Error ==> {e}")
        traceback.print_exc()
        return False, {}, f"{e}"


def create_vendor_from_recipient(cust_id: str, vendor_info: dict, invoice_table):
    """
    Creates a new Vendor record from an existing load recipient in DUKE-User-Invoices for this user;
    :param cust_id: str, (required) DUKE user ID;
    :param vendor_info: dict, dictionary containing (company_name, address, address2, phone, contact, city, state, postal, country);
    :param invoice_table: boto3.resources.factory.dynamodb.Table;
    :return: Boolean.
    """
    func = create_vendor_from_recipient.__name__
    print(f"[{func}] activated")
    try:
        city = vendor_info.get('city')
        state = vendor_info.get('state')
        country = vendor_info.get('country')
        street1 = vendor_info.get('address')
        street2 = vendor_info.get('address2')
        contact = vendor_info.get('contact')
        phone = vendor_info.get('phone')
        postal = vendor_info.get('postal')

        if city is not None:
            city = city.upper()
        if state is not None:
            state = state.upper()
        if country is not None:
            country = country.upper()
        if street1 is not None:
            street1 = street1.upper()
        if street2 is not None:
            street2 = street2.upper()
        if contact is not None:
            contact = contact.upper()

        vid = gen_random_sha()[:12]
        new_vendor = {
            "cust_id": cust_id.upper(),
            "vendor_name": vendor_info['company_name'].upper(),
            "contact": contact,
            "vendor_id": vid,
            "vendor_email": vendor_info['vendor_email'].upper(),
            "phone": phone,
            "city": city,
            "state": state,
            "postal": postal,
            "country": country,
            "address": [],
            "balance": "0.0",
            "invoices": [],
            "tax_id": None
        }
        if street1 is not None and street2 is not None:
            new_vendor["address"].extend([street1, street2])
        elif street1 is not None:
            new_vendor["address"].append(street1)

        res = invoice_table.put_item(Item=new_vendor)
        if res['ResponseMetadata']['HTTPStatusCode'] != 200:
            print(f"[PUT NEW VENDOR ERROR] {res}")
            raise Exception(f"Error putting new vendor object; AWS Response Code: {res['ResponseMetadata']['HTTPStatusCode']}")

        return True, new_vendor, ""
    except Exception as e:
        print(f"[ERROR] {func} Error ==> {e}")
        traceback.print_exc()
        return True, {}, f"{e}"


def batch_update_vendor_record(invoice_info_array, vendor_info, invoice_table):
    func = batch_update_vendor_record.__name__
    try:
        ven_name = vendor_info['vendor_name']
        balance = float(vendor_info['balance'])
        for invoice_info in invoice_info_array:
            filenames = invoice_info['filename']
            if not isinstance(filenames, list):
                filenames = [filenames]
            data = {
                "amount": invoice_info['rate'],
                "bill_date": invoice_info['bill_date'],
                "due_date": invoice_info['due_date'],
                "bill_to": ven_name,
                "doc_sha": invoice_info['doc_sha'],
                "filenames": filenames,
                "invoice_id": invoice_info['invoice_number'],
                "paid_status": False
            }
            if "reference_id" in invoice_info.keys():
                data.update({
                    'reference_id': invoice_info['reference_id']
                })
            if "load_uuid" in invoice_info.keys():
                data.update({
                    'load_uuid': invoice_info['load_uuid']
                })

            balance += float(invoice_info['rate'])
            vendor_info['invoices'].append(data)

        vendor_info.update({
            "balance": str(balance)
        })
        res = invoice_table.put_item(Item=vendor_info)
        print(f"[INFO] vendor update res = {res}")
        if res['ResponseMetadata']['HTTPStatusCode'] in [200, 202, 204]:
            return True, ""
        else:
            raise Exception(f"invoice_table.put_item['ResponseMetadata']['HTTPStatusCode'] = {res['ResponseMetadata']['HTTPStatusCode']}")
    except Exception as e:
        print(f"[ERROR] {func} Error ==> {e}")
        traceback.print_exc()
        return False, f"{e}"

