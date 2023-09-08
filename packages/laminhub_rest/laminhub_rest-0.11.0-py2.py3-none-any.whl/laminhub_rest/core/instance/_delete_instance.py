from typing import Optional, Union

from laminhub_rest.connector import connect_hub_with_auth
from laminhub_rest.core.account._crud import sb_select_account_by_handle
from laminhub_rest.core.instance._crud import (
    sb_delete_instance,
    sb_select_instance_by_name,
)


def delete_instance(
    *,
    owner: str,  # owner handle
    name: str,  # instance name
    _email: Optional[str] = None,
    _password: Optional[str] = None,
    _access_token: Optional[str] = None,
) -> Union[None, str]:
    hub = connect_hub_with_auth(
        email=_email, password=_password, access_token=_access_token
    )
    try:
        # get account
        account = sb_select_account_by_handle(owner, hub)
        if account is None:
            return "account-not-exists"

        # get instance
        instance = sb_select_instance_by_name(account["id"], name, hub)
        if instance is None:
            return "instance-not-reachable"

        sb_delete_instance(instance["id"], hub)

        # TODO: delete storage if no other instances use it
        return None
    except Exception as e:
        return str(e)
    finally:
        hub.auth.sign_out()
