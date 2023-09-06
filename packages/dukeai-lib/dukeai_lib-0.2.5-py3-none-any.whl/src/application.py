import json
import traceback
from chalice import Response, ForbiddenError
from src.utilities import DecimalEncoder


# NEW CHECK_ACCESS - v2.0.1
def check_access(allowed_groups, claims, req_id="NULL_REQ_ID", cust_id=None):
    try:
        print(claims)
        caller = claims.get('cognito:username')  # Gives user id, which is email or Google_XXX
        caller_groups = claims.get('cognito:groups')
        if not caller_groups:
            # sendEmail("User Access Forbidden", f"{caller} is not a member of any group")
            raise ForbiddenError(f"[({req_id}) FAILED]: {caller} is not a member of any group")

        if type(caller_groups) is str:
            caller_groups = caller_groups.split(",")

        is_allowed = False
        is_admin = False
        for group in caller_groups:
            if group in ["users", "annotators", "admin", "accountants"]:
                is_allowed = True
            if group in ["annotators", "admin", "accountants"]:
                is_admin = True
        if not is_allowed:
            raise ForbiddenError(f"[({req_id}) FAILED] Access Forbidden. Caller {caller} not in a Cognito group")

        # Is it an allowed group
        if not any(group in allowed_groups for group in caller_groups):
            raise ForbiddenError(f"[({req_id}) FAILED]: Access Denied. User group not allowed for this route.")

        # Need the email, and return the email
        claimed_email = claims.get("email")
        if is_admin:
            return claimed_email, caller_groups
        if claimed_email is not None:
            claimed_email = claimed_email.upper()
            if cust_id is not None:
                cust_id = cust_id.upper()
            if cust_id != claimed_email:
                raise ForbiddenError(f"[({req_id}) FAILED]: Access denied. Cust id and caller email don't match.")
        else:
            raise ForbiddenError(f"[({req_id}) FAILED]: Access denied. No email in claims.")

        return claimed_email, caller_groups
    except ForbiddenError as fe:
        print(fe)
        return None, None
    except Exception as e:
        print(f"Unknown `check_access` function exception ==> {e}")
        traceback.print_exc()
        return None, None


def api_response(status_code,
                 body=None,
                 msg=None,
                 headers=None
                 ):
    """
    Returns a Chalice response object. If body is specified, it will return a JSON response, else a string message
    If both body and msg are specified, the msg will be embedded into the dict and a JSON returned;
    :param status_code: 200 | 4XX | 5XX;
    :param body: (optional) A dictionary to return as JSON;
    :param msg: (optional) A simple string message;
    :param headers: ;
    :return: Response(body, status_code)
    """
    if body is not None and msg is not None:
        body['msg'] = msg
        return Response(
            json.dumps(body, cls=DecimalEncoder),
            status_code=status_code,
            headers=headers
        )
    elif body is not None:
        return Response(
            json.dumps(body, cls=DecimalEncoder),
            status_code=status_code,
            headers=headers
        )
    elif msg is not None:
        return Response(
            msg,
            status_code=status_code,
            headers=headers
        )
    else:
        return Response(
            f"Response: {str(status_code)}",
            status_code=status_code,
            headers=headers
        )
