import json
import decimal
import traceback
import urllib.parse
from dukeai_lib.globals import CUSTOMER_EMAIL_FOOTER


def send_email(
        subject: str,
        body: str,
        recipient: str,
        email_sender: str,
        footer: bool,
        email_client,
        body2="",
        body3="",
        body4="",
        body5="",
        body6="",
        body7="",
        body8=""
):
    func = send_email.__name__
    if isinstance(recipient, str):
        recipient = [recipient]

    if body2 is None:
        body2 = ""
    if body3 is None:
        body3 = ""
    if body4 is None:
        body4 = ""
    if body5 is None:
        body5 = ""
    if body6 is None:
        body6 = ""
    if body7 is None:
        body7 = ""
    if body8 is None:
        body8 = ""

    if footer:
        body_html = f"""
        <html>
        <head></head>
        <body>
        <p>{body}</p>
        <p>{body2}</p>
        <p>{body3}</p>
        <p>{body4}</p>
        <p>{body5}</p>
        <p>{body6}</p>
        <p>{body7}</p>
        <p>{body8}</p>
        {CUSTOMER_EMAIL_FOOTER}
        </body>
        </html>
        """
    else:
        body_html = f"""
        <html>
        <head></head>
        <body>
        <p>{body}</p>
        <p>{body2}</p>
        <p>{body3}</p>
        <p>{body4}</p>
        <p>{body5}</p>
        <p>{body6}</p>
        <p>{body7}</p>
        <p>{body8}</p>
        </body>
        </html>
        """
    try:
        response = email_client.send_email(
            Destination={
                'ToAddresses': recipient
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': "UTF-8",
                        'Data': body_html,
                    },
                    'Text': {
                        'Charset': "UTF-8",
                        'Data': (str(body_html)),
                    }
                },
                'Subject': {
                    'Charset': "UTF-8",
                    'Data': subject,
                },
            },
            Source=email_sender
        )
        print(f"Email sent! Message ID: {response['MessageId']}")

        return True, response, ""

    except Exception as e:
        print(f"[ERROR] {func} Error ==> {e}")
        traceback.print_exc()
        return False, {}, f"{e}"


def gen_single_button_html(button_text, button_header, link, alignment, button_color, button_text_color):
    link_style1 = f"""
    style="padding: 8px 12px; font-size: 14px; color: {button_text_color}; font-weight:bold; display:inline-block;"
    """
    button = f"""
    <br>
    <br>
    <table width="100%" cellspacing="0" cellpadding="0", border="0", align="{alignment}" style="margin-bottom:50px; max-width:700px; width:100%;">
        <tr>
            <th>{button_header}</th>
        </tr>
        <tr>

            <td style="border-radius: 2px; text-align:center; vertical-align:middle">
                <table cellspacing="0" cellpadding="0", align="center">
                    <tr style="text-align:center; vertical-align:middle">
                        <td class="button" bgcolor="{button_color}" style="font-family:Arial,Helvetica,sans-serif; font-size:14px; font-weight:bold; display:inline-block; background-clip:padding-box;">
                            <a class=”link” href="{link}" target="_blank" {link_style1}>
                                {button_text}             
                            </a>
                        </td>
                    </tr>
                </table>
            </td>

        </tr>
    </table>
    <br>
    <br>
    <br>
    <br>
    <br>
    <br>
    """
    return button


def gen_three_button_html(bd_array: list):
    """
    Generates raw HTML for an inline 3 button email insert;
    Expected input for 'bd_array' is something like:
    bd_array=[
        {
            'button_header': 'Button 1',
            'button_text': 'option 1',
            'link': "https://duke.ai/accountant-portal/signin/index.html"
        },
        {
            'button_header': 'Button 2',
            'button_text': 'option 2',
            'link': "https://duke.ai/accountant-portal/signin/index.html"
        },
        {
            'button_header': 'Button 3',
            'button_text': 'option 3',
            'link': "https://duke.ai/accountant-portal/signin/index.html"
        }
    ]
    """
    func = gen_three_button_html.__name__
    try:
        link_style1 = """
        style="padding: 8px 12px; font-size: 14px; color: #ffffff; font-weight:bold; display:inline-block;"
        """
        table = f"""
        <table width="100%" cellspacing="4" cellpadding="4", border="0", align="center" style="margin-bottom:50px; max-width:700px; width:100%;">
            <tr>
                <th>{bd_array[0]['button_header']}</th>
                <th>{bd_array[1]['button_header']}</th>
                <th>{bd_array[2]['button_header']}</th>
            </tr>
            <tr>

                <td style="border-radius: 2px; text-align:center; vertical-align:middle">
                    <table cellspacing="0" cellpadding="0", align="center">
                        <tr style="text-align:center; vertical-align:middle">
                            <td class="button" bgcolor="#1F83FF" style="font-family:Arial,Helvetica,sans-serif; font-size:14px; font-weight:bold; display:inline-block; background-clip:padding-box;">
                                <a class=”link” href="{bd_array[0]['link']}" target="_blank" {link_style1}>
                                    {bd_array[0]['button_text']}             
                                </a>
                            </td>
                        </tr>
                    </table>
                </td>

                <td style="border-radius: 2px; text-align:center; vertical-align:middle">
                    <table cellspacing="0" cellpadding="0", align="center">
                        <tr style="text-align:center; vertical-align:middle">
                            <td class="button" bgcolor="#1F83FF" style="font-family:Arial,Helvetica,sans-serif; font-size:14px; font-weight:bold; display:inline-block; background-clip:padding-box;">
                                <a class=”link” href="{bd_array[1]['link']}" target="_blank" {link_style1}>
                                    {bd_array[1]['button_text']}             
                                </a>
                            </td>
                        </tr>
                    </table>
                </td>

                <td style="border-radius: 2px; text-align:center; vertical-align:middle">
                    <table cellspacing="0" cellpadding="0", align="center">
                        <tr style="text-align:center; vertical-align:middle">
                            <td class="button" bgcolor="#1F83FF" style="font-family:Arial,Helvetica,sans-serif; font-size:14px; font-weight:bold; display:inline-block; background-clip:padding-box;">
                                <a class=”link” href="{bd_array[2]['link']}" target="_blank" {link_style1}>
                                    {bd_array[2]['button_text']}             
                                </a>
                            </td>
                        </tr>
                    </table>
                </td>

            </tr>
        </table>
        """

        return True, table
    except Exception as e:
        print(f"[ERROR] {func} Error ==> {e}")
        traceback.print_exc()
        return False, ""


def format_bucket_url(bucket_name: str, full_object_name: str):
    func = format_bucket_url.__name__
    try:
        full_object_name = urllib.parse.quote(full_object_name)
        response = f"https://{bucket_name}.s3.amazonaws.com/{full_object_name}"
        print(f"[{func}] Returning {response}")
        return response
    except Exception as e:
        print(f"[ERROR] {func} Error ==> {e}")
        traceback.print_exc()
        return None


def multi_load_confirmation_email(subject, body, recipient, all_response_data, email_sender, email_client, body2="", body3=""):
    func = multi_load_confirmation_email.__name__
    try:
        if isinstance(recipient, str):
            recipient = [recipient]

        load_responses = list()
        for load_resp in all_response_data:
            idx = all_response_data.index(load_resp)

            button_data = [
                {
                    'button_header': 'Invoice',
                    'button_text': 'Download PDF',
                    'link': load_resp['duke_invoice_url']
                },
                {
                    'button_header': 'DUKE Verified Score',
                    'button_text': 'Download PDF',
                    'link': load_resp['score_report_url']
                },
                {
                    'button_header': 'Load Documents',
                    'button_text': 'Download PDF',
                    'link': load_resp['load_document_link']
                }
            ]
            success, table = gen_three_button_html(button_data)
            if not success:
                raise Exception(f"gen_three_button_html encountered an error")

            if load_resp['vendor_bill_no'] not in ["0000", "00", "0"]:
                load_responses.append(
                    f"""
                    <p>Rate Confirmation Reference #: {load_resp['load_reference']}</p>
                    <p>DUKE.ai Invoice #: {load_resp['duke_invoice_no']}</p>
                    <p>Vendor Bill #: {load_resp['vendor_bill_no']}</p>
                    <p>DUKE.ai Load reference #: {load_resp['load_id']}</p>
                    <p>Total: ${load_resp['amount']}</p>
                    {table}
                    """
                )

            else:
                # """
                # <p>Downloadable Invoice PDF: {load_resp['duke_invoice_url']}</p>
                # <p>Downloadable Load Acceptance Score PDF: {load_resp['score_report_url']}</p>
                # <p>Downloadable Load Document PDF: {load_resp['load_document_link']}</p>
                # """
                load_responses.append(
                    f"""
                    <p>Rate Confirmation Reference #: {load_resp['load_reference']}</p>
                    <p>DUKE.ai Invoice #: {load_resp['duke_invoice_no']}</p>
                    <p>DUKE.ai Load reference #: {load_resp['load_id']}</p>
                    <p>Total: ${load_resp['amount']}</p>
                    {table}
                    """
                )

            if idx != (len(all_response_data) - 1):
                load_responses.append(
                    "<p>-----------------------------------</p>"
                )
            else:
                load_responses.append("<p></p>")

        load_responses.append(
            f"""
            <p></p>
            <p>-----------------------------------</p>
            <p></p>
            <p>Please contact Support@Duke.ai if you have any questions, and thank you for trucking with DUKE.ai!</p>
            """
        )

        body_string = "".join(load_responses)

        body_html = f"""
        <html>
        <head></head>
        <body>
        <p>{body}</p>
        <p>{body2}</p>
        <p>{body3}</p>
        <p></p>
        {body_string}
        </body>
        </html>
          """

        response = email_client.send_email(
            Destination={
                'ToAddresses': recipient
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': "UTF-8",
                        'Data': body_html,
                    },
                    'Text': {
                        'Charset': "UTF-8",
                        'Data': (str(body_html)),
                    }
                },
                'Subject': {
                    'Charset': "UTF-8",
                    'Data': subject,
                },
            },
            Source=email_sender
        )
        print(f"[INFO] {func} Email sent! Message ID: {response}")
        return True, response, ""
    except Exception as e:
        print(f"[ERROR] {func} Error ==> {e}")
        traceback.print_exc()
        return False, None, f"{e}"


def multi_load_confirmation_email_v2(
        subject: str,
        body: str,
        recipient: str,
        invoice_response_data: list,
        bol_response_data: list,
        email_client,
        email_sender,
        body2="",
        body3=""
):
    function_name = multi_load_confirmation_email_v2.__name__
    if isinstance(recipient, str):
        recipient = [recipient]

    bol_responses = list()
    for bol_res in bol_response_data:
        idx = bol_response_data.index(bol_res)
        button = gen_single_button_html(
            button_text="Download",
            button_header="BOL Load documents",
            link=bol_res['load_document_link'],
            alignment="center",
            button_color="#1F83FF",
            button_text_color="#ffffff"
        )
        bol_responses.append(
            f"""
            <p>Bill of Lading Reference #: {bol_res['kvt_data']['identifier']}</p>
            <p>Total: ${bol_res['kvt_data']['charges']}</p>
            {button}
            """
        )
        if idx != (len(bol_responses) - 1):
            bol_responses.append(
                "<p>-----------------------------------</p>"
            )
        else:
            if len(invoice_response_data) >= 1:
                bol_responses.append(
                    "<p>-----------------------------------</p>"
                )
            else:
                bol_responses.append("<p></p>")

    load_responses = list()
    load_responses.extend(bol_responses)
    for load_resp in invoice_response_data:
        idx = invoice_response_data.index(load_resp)

        button_data = [
            {
                'button_header': 'Invoice',
                'button_text': 'Download PDF',
                'link': load_resp['duke_invoice_url']
            },
            {
                'button_header': 'DUKE Verified Score',
                'button_text': 'Download PDF',
                'link': load_resp['score_report_url']
            },
            {
                'button_header': 'Invoiced Load Documents',
                'button_text': 'Download PDF',
                'link': load_resp['load_document_link']
            }
        ]
        success, table = gen_three_button_html(button_data)
        if not success:
            raise Exception(f"gen_three_button_html encountered an error")

        if load_resp['vendor_bill_no'] not in ["0000", "00", "0"]:
            load_responses.append(
                f"""
                <p>Rate Confirmation Reference #: {load_resp['load_reference']}</p>
                <p>DUKE.ai Invoice #: {load_resp['duke_invoice_no']}</p>
                <p>Vendor Bill #: {load_resp['vendor_bill_no']}</p>
                <p>DUKE.ai Load reference #: {load_resp['load_id']}</p>
                <p>Total: ${load_resp['amount']}</p>
                {table}
                """
            )

        else:
            # """
            # <p>Downloadable Invoice PDF: {load_resp['duke_invoice_url']}</p>
            # <p>Downloadable Load Acceptance Score PDF: {load_resp['score_report_url']}</p>
            # <p>Downloadable Load Document PDF: {load_resp['load_document_link']}</p>
            # """
            load_responses.append(
                f"""
                <p>Rate Confirmation Reference #: {load_resp['load_reference']}</p>
                <p>DUKE.ai Invoice #: {load_resp['duke_invoice_no']}</p>
                <p>DUKE.ai Load reference #: {load_resp['load_id']}</p>
                <p>Total: ${load_resp['amount']}</p>
                {table}
                """
            )

        if idx != (len(invoice_response_data) - 1):
            load_responses.append(
                "<p>-----------------------------------</p>"
            )
        else:
            load_responses.append("<p></p>")

    load_responses.append(
        f"""
        <p></p>
        <p>-----------------------------------</p>
        <p></p>
        <p>Please contact Support@Duke.ai if you have any questions, and thank you for trucking with DUKE.ai!</p>
        """
    )

    body_string = "".join(load_responses)

    body_html = f"""
    <html>
    <head></head>
    <body>
    <p>{body}</p>
    <p>{body2}</p>
    <p>{body3}</p>
    <p></p>
    {body_string}
    </body>
    </html>
      """
    try:
        response = email_client.send_email(
            Destination={
                'ToAddresses': recipient
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': "UTF-8",
                        'Data': body_html,
                    },
                    'Text': {
                        'Charset': "UTF-8",
                        'Data': (str(body_html)),
                    }
                },
                'Subject': {
                    'Charset': "UTF-8",
                    'Data': subject,
                },
            },
            Source=email_sender
        )
        print(f"[INFO] {function_name} Email sent! Message ID: {response}")
        return response
    except Exception as e:
        print(f"[ERROR] {function_name} Error ==> {e}")
        traceback.print_exc()
        return None


def send_schedule_email(
        subject,
        body,
        recipient,
        duke_customer,
        pdf_url,
        platform_vendor_id,
        transaction_fee,
        factoring_fee,
        all_response_data,
        email_sender,
        email_client,
        zoho=False,
        quickbooks=False
):
    func = send_schedule_email.__name__
    try:
        if isinstance(recipient, str):
            recipient = [recipient]

        load_responses = list()
        for load_resp in all_response_data:
            idx = all_response_data.index(load_resp)
            report_button = gen_single_button_html(
                button_header=f"DUKE Verified Score - {load_resp['load_reference']}",
                button_text="Download PDF",
                link=load_resp['score_report_url'],
                alignment="left",
                button_color="#1F83FF",
                button_text_color="#ffffff"
            )
            load_responses.append(
                f"""
                <p>Your bill number: {load_resp['vendor_bill_no']}</p>
                <p>Carrier's DUKE Invoice number: {load_resp['duke_invoice_no']}</p>
                <p>Load reference number: {load_resp['load_reference']}</p>
                <p>Rate Confirmation amount: {load_resp['amount']}</p>
                <p>{report_button}</p>
                """
            )
            if idx != (len(all_response_data) - 1):
                load_responses.append(
                    "<p>-----------------------------------</p>"
                )
            else:
                load_responses.append("<p></p>")

        platform = ""
        if zoho and not quickbooks:
            platform = "Zoho"
        elif quickbooks and not zoho:
            platform = "Quickbooks"
        elif not zoho and not quickbooks:
            raise Exception(f"Both values of <zoho> and <quickbooks> are set to False! One must be True.")

        schedule_button = gen_single_button_html(
            button_header="Schedule of Invoices",
            button_text="Download PDF",
            link=pdf_url,
            alignment="left",
            button_color="#1F83FF",
            button_text_color="#ffffff"
        )

        body_string = "".join(load_responses)
        body_text = str(body)
        body_html = f"""
        <html>
        <head>Schedule of Invoices Purchased from {duke_customer.upper()}</head>
        <body>
        <p>{body_text}</p>
        <p></p>
        <p>For your convenience, please note: the total amount paid to your client on this schedule includes a transaction fee deduction of {transaction_fee}, as well as a factoring fee deduction of {factoring_fee}% as specified in your account with DUKE.ai. 
        The bill that exists in your {platform} account does not include these deductions, and will need to be updated at the time of payment. Any custom line items that you add, or changes to the data or amount will reflect on the Carrier's
        Invoice in the DUKE system within 24 hours.</p>
        <p></p>
        <p>DUKE customer email address: {duke_customer.upper()}</p>
        <p>{platform} vendor ID for customer: {platform_vendor_id}</p>
        <p>{schedule_button}</p>
        <p></p>
        <p>-----------------------------------</p>
        <p></p>
        {body_string}
        <p>Thanks for trucking with DUKE.ai!</p>
        <p>Support@DUKE.ai</p>
        <p>831.350.4529</p>
        </body>
        </html>
        """

        response = email_client.send_email(
            Destination={
                'ToAddresses': recipient
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': "UTF-8",
                        'Data': body_html,
                    },
                    'Text': {
                        'Charset': "UTF-8",
                        'Data': str(body_text),
                    },
                },
                'Subject': {
                    'Charset': "UTF-8",
                    'Data': subject,
                },
            },
            Source=email_sender
        )
        print(f"[INFO] Email sent! Message ID: {response}")
        return True, response, ""
    except Exception as e:
        print(f"[ERROR] {func} Error ==> {e}")
        traceback.print_exc()
        return False, None, ""


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return float(o)
        return super(DecimalEncoder, self).default(o)
