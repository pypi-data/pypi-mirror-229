from typing import Optional, Union

from laminhub_rest.connector import connect_hub_with_auth
from laminhub_rest.core.instance._crud import sb_update_instance
from laminhub_rest.utils._query import filter_null_from_dict


def update_instance(
    instance_id: str,
    account_id: Union[str, None] = None,
    public: Optional[bool] = False,
    description: Optional[str] = None,
    _email: Optional[str] = None,
    _password: Optional[str] = None,
    _access_token: Optional[str] = None,
) -> Union[None, str]:
    hub = connect_hub_with_auth(
        email=_email, password=_password, access_token=_access_token
    )
    try:
        fields = filter_null_from_dict(
            {
                "account_id": account_id,
                "public": public,
                "description": description,
            }
        )

        instance = sb_update_instance(instance_id, fields, hub)
        if instance is None:
            return "instance-not-updated"

        return None
    except Exception as e:
        raise e
    finally:
        hub.auth.sign_out()
