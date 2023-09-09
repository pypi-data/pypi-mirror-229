class Bulk:

    def __init__(self, mv_sdk, base_url: str, domain: str, **kwargs: dict):
        """
        Initialize the Asset Domain
        """
        super(Bulk, self)
        self.mv_sdk = mv_sdk
        self.base_url = base_url
        self.domain = domain
    
    def post(self, params=None, data=None, headers=None, auth=None, object_id=None,
             domain_id=None, domain_action=None, bulk=False):
        """

        """
        headers = headers or {}

        return self.mv_sdk.request(
            'post',
            self.base_url,
            self.domain,
            params=params,
            data=data,
            headers=headers,
            auth=auth,
            object_id=object_id,
            domain_id=domain_id,
            domain_action=domain_action
        )
