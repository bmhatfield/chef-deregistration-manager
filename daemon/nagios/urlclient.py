class URLClient():
    """
    Issues HTTP/HTTPS requests against the Nagios URL API (using GET params)
    """    
    def __init__(self, hostname="monitor", protocol="https", user=None, password=None, cgi_path="/nagios/cgi-bin/cmd.cgi"):
        self.hostname = hostname
        self.protocol = protocol
        self.cgi_path = cgi_path

        self.user = user
        self.password = password

    def downtime(self, host, message="Automated Downtime", start_time=None, end_time=None):
        params["cmd_typ"] = 55
        params["cmd_mod"] = 2
        params["trigger"] = 0
        params["fixed"] = 1
        params["hours"] = 2
        params["minutes"] = 0
        params["childoptions"] = 0
        params["btnSubmit"] = "Commit"
        
        params["host"] = host
        # params["com_data"] = urlencode(message) -- TODO: Use actual urlencode function
        params["start_time"] = start_time
        params["end_time"] = end_time

        self.request(params)

    def request(self, param_dict):
        # TODO: zip param_dict to key=value, and join with &, and set to "request_params"
        request_url = "%s://%s%s?%s" % (self.protocol, self.hostname, self.cgi_path, request_params)

        if self.user is not None and self.password is not None:
            # TODO: Issue HTTP/Auth request
        else:
            # TODO: Issue unauthenticated request