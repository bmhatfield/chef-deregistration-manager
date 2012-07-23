#! /usr/bin/env python
'''Python CGI interface to Nagios.

Ever want to control Nagios from some place that *wasn't* the Nagios
server itself?  Ever notice that the web front-end is kind of painful
to automate?  Ever have that dream where ... Uh, I mean, let's make
Nagios controllable programatically.

Expects python-2.6.2 or equivalent for urllib2.
'''

import urllib, urllib2, os, time

class Nagcgi:
    # {{{ class variables (all of the nagios command identifiers from common.h)

    _commit = 2
    CMD_ADD_HOST_COMMENT = 1
    CMD_DEL_HOST_COMMENT = 2
    CMD_ADD_SVC_COMMENT = 3
    CMD_DEL_SVC_COMMENT = 4
    CMD_ENABLE_SVC_CHECK = 5
    CMD_DISABLE_SVC_CHECK = 6
    CMD_SCHEDULE_SVC_CHECK = 7
    CMD_DELAY_SVC_NOTIFICATION = 9
    CMD_DELAY_HOST_NOTIFICATION = 10
    CMD_DISABLE_NOTIFICATIONS = 11
    CMD_ENABLE_NOTIFICATIONS = 12
    CMD_RESTART_PROCESS = 13
    CMD_SHUTDOWN_PROCESS = 14
    CMD_ENABLE_HOST_SVC_CHECKS = 15
    CMD_DISABLE_HOST_SVC_CHECKS = 16
    CMD_SCHEDULE_HOST_SVC_CHECKS = 17
    CMD_DEL_ALL_HOST_COMMENTS = 20
    CMD_DEL_ALL_SVC_COMMENTS = 21
    CMD_ENABLE_SVC_NOTIFICATIONS = 22
    CMD_DISABLE_SVC_NOTIFICATIONS = 23
    CMD_ENABLE_HOST_NOTIFICATIONS = 24
    CMD_DISABLE_HOST_NOTIFICATIONS = 25
    CMD_ENABLE_ALL_NOTIFICATIONS_BEYOND_HOST = 26
    CMD_DISABLE_ALL_NOTIFICATIONS_BEYOND_HOST = 27
    CMD_ENABLE_HOST_SVC_NOTIFICATIONS = 28
    CMD_DISABLE_HOST_SVC_NOTIFICATIONS = 29
    CMD_PROCESS_SERVICE_CHECK_RESULT = 30
    CMD_SAVE_STATE_INFORMATION = 31
    CMD_READ_STATE_INFORMATION = 32
    CMD_ACKNOWLEDGE_HOST_PROBLEM = 33
    CMD_ACKNOWLEDGE_SVC_PROBLEM = 34
    CMD_START_EXECUTING_SVC_CHECKS = 35
    CMD_STOP_EXECUTING_SVC_CHECKS = 36
    CMD_START_ACCEPTING_PASSIVE_SVC_CHECKS = 37
    CMD_STOP_ACCEPTING_PASSIVE_SVC_CHECKS = 38
    CMD_ENABLE_PASSIVE_SVC_CHECKS = 39
    CMD_DISABLE_PASSIVE_SVC_CHECKS = 40
    CMD_ENABLE_EVENT_HANDLERS = 41
    CMD_DISABLE_EVENT_HANDLERS = 42
    CMD_ENABLE_HOST_EVENT_HANDLER = 43
    CMD_DISABLE_HOST_EVENT_HANDLER = 44
    CMD_ENABLE_SVC_EVENT_HANDLER = 45
    CMD_DISABLE_SVC_EVENT_HANDLER = 46
    CMD_ENABLE_HOST_CHECK = 47
    CMD_DISABLE_HOST_CHECK = 48
    CMD_START_OBSESSING_OVER_SVC_CHECKS = 49
    CMD_STOP_OBSESSING_OVER_SVC_CHECKS = 50
    CMD_REMOVE_HOST_ACKNOWLEDGEMENT = 51
    CMD_REMOVE_SVC_ACKNOWLEDGEMENT = 52
    CMD_SCHEDULE_FORCED_HOST_SVC_CHECKS = 53
    CMD_SCHEDULE_FORCED_SVC_CHECK = 54
    CMD_SCHEDULE_HOST_DOWNTIME = 55
    CMD_SCHEDULE_SVC_DOWNTIME = 56
    CMD_ENABLE_HOST_FLAP_DETECTION = 57
    CMD_DISABLE_HOST_FLAP_DETECTION = 58
    CMD_ENABLE_SVC_FLAP_DETECTION = 59
    CMD_DISABLE_SVC_FLAP_DETECTION = 60
    CMD_ENABLE_FLAP_DETECTION = 61
    CMD_DISABLE_FLAP_DETECTION = 62
    CMD_ENABLE_HOSTGROUP_SVC_NOTIFICATIONS = 63
    CMD_DISABLE_HOSTGROUP_SVC_NOTIFICATIONS = 64
    CMD_ENABLE_HOSTGROUP_HOST_NOTIFICATIONS = 65
    CMD_DISABLE_HOSTGROUP_HOST_NOTIFICATIONS = 66
    CMD_ENABLE_HOSTGROUP_SVC_CHECKS = 67
    CMD_DISABLE_HOSTGROUP_SVC_CHECKS = 68
    CMD_FLUSH_PENDING_COMMANDS = 77
    CMD_DEL_HOST_DOWNTIME = 78
    CMD_DEL_SVC_DOWNTIME = 79
    CMD_ENABLE_FAILURE_PREDICTION = 80
    CMD_DISABLE_FAILURE_PREDICTION = 81
    CMD_ENABLE_PERFORMANCE_DATA = 82
    CMD_DISABLE_PERFORMANCE_DATA = 83
    CMD_SCHEDULE_HOSTGROUP_HOST_DOWNTIME = 84
    CMD_SCHEDULE_HOSTGROUP_SVC_DOWNTIME = 85
    CMD_SCHEDULE_HOST_SVC_DOWNTIME = 86
    CMD_PROCESS_HOST_CHECK_RESULT = 87
    CMD_START_EXECUTING_HOST_CHECKS = 88
    CMD_STOP_EXECUTING_HOST_CHECKS = 89
    CMD_START_ACCEPTING_PASSIVE_HOST_CHECKS = 90
    CMD_STOP_ACCEPTING_PASSIVE_HOST_CHECKS = 91
    CMD_ENABLE_PASSIVE_HOST_CHECKS = 92
    CMD_DISABLE_PASSIVE_HOST_CHECKS = 93
    CMD_START_OBSESSING_OVER_HOST_CHECKS = 94
    CMD_STOP_OBSESSING_OVER_HOST_CHECKS = 95
    CMD_SCHEDULE_HOST_CHECK = 96
    CMD_SCHEDULE_FORCED_HOST_CHECK = 98
    CMD_START_OBSESSING_OVER_SVC = 99
    CMD_STOP_OBSESSING_OVER_SVC = 100
    CMD_START_OBSESSING_OVER_HOST = 101
    CMD_STOP_OBSESSING_OVER_HOST = 102
    CMD_ENABLE_HOSTGROUP_HOST_CHECKS = 103
    CMD_DISABLE_HOSTGROUP_HOST_CHECKS = 104
    CMD_ENABLE_HOSTGROUP_PASSIVE_SVC_CHECKS = 105
    CMD_DISABLE_HOSTGROUP_PASSIVE_SVC_CHECKS = 106
    CMD_ENABLE_HOSTGROUP_PASSIVE_HOST_CHECKS = 107
    CMD_DISABLE_HOSTGROUP_PASSIVE_HOST_CHECKS = 108
    CMD_ENABLE_SERVICEGROUP_SVC_NOTIFICATIONS = 109
    CMD_DISABLE_SERVICEGROUP_SVC_NOTIFICATIONS = 110
    CMD_ENABLE_SERVICEGROUP_HOST_NOTIFICATIONS = 111
    CMD_DISABLE_SERVICEGROUP_HOST_NOTIFICATIONS = 112
    CMD_ENABLE_SERVICEGROUP_SVC_CHECKS = 113
    CMD_DISABLE_SERVICEGROUP_SVC_CHECKS = 114
    CMD_ENABLE_SERVICEGROUP_HOST_CHECKS = 115
    CMD_DISABLE_SERVICEGROUP_HOST_CHECKS = 116
    CMD_ENABLE_SERVICEGROUP_PASSIVE_SVC_CHECKS = 117
    CMD_DISABLE_SERVICEGROUP_PASSIVE_SVC_CHECKS = 118
    CMD_ENABLE_SERVICEGROUP_PASSIVE_HOST_CHECKS = 119
    CMD_DISABLE_SERVICEGROUP_PASSIVE_HOST_CHECKS = 120
    CMD_SCHEDULE_SERVICEGROUP_HOST_DOWNTIME = 121
    CMD_SCHEDULE_SERVICEGROUP_SVC_DOWNTIME = 122
    CMD_CHANGE_GLOBAL_HOST_EVENT_HANDLER = 123
    CMD_CHANGE_GLOBAL_SVC_EVENT_HANDLER = 124
    CMD_CHANGE_HOST_EVENT_HANDLER = 125
    CMD_CHANGE_SVC_EVENT_HANDLER = 126
    CMD_CHANGE_HOST_CHECK_COMMAND = 127
    CMD_CHANGE_SVC_CHECK_COMMAND = 128
    CMD_CHANGE_NORMAL_HOST_CHECK_INTERVAL = 129
    CMD_CHANGE_NORMAL_SVC_CHECK_INTERVAL = 130
    CMD_CHANGE_RETRY_SVC_CHECK_INTERVAL = 131
    CMD_CHANGE_MAX_HOST_CHECK_ATTEMPTS = 132
    CMD_CHANGE_MAX_SVC_CHECK_ATTEMPTS = 133
    CMD_SCHEDULE_AND_PROPAGATE_TRIGGERED_HOST_DOWNTIME = 134
    CMD_ENABLE_HOST_AND_CHILD_NOTIFICATIONS = 135
    CMD_DISABLE_HOST_AND_CHILD_NOTIFICATIONS = 136
    CMD_SCHEDULE_AND_PROPAGATE_HOST_DOWNTIME = 137
    CMD_ENABLE_SERVICE_FRESHNESS_CHECKS = 138
    CMD_DISABLE_SERVICE_FRESHNESS_CHECKS = 139
    CMD_ENABLE_HOST_FRESHNESS_CHECKS = 140
    CMD_DISABLE_HOST_FRESHNESS_CHECKS = 141
    CMD_SET_HOST_NOTIFICATION_NUMBER = 142
    CMD_SET_SVC_NOTIFICATION_NUMBER = 143
    CMD_CHANGE_HOST_CHECK_TIMEPERIOD = 144
    CMD_CHANGE_SVC_CHECK_TIMEPERIOD = 145
    CMD_PROCESS_FILE = 146
    CMD_CHANGE_CUSTOM_HOST_VAR = 147
    CMD_CHANGE_CUSTOM_SVC_VAR = 148
    CMD_CHANGE_CUSTOM_CONTACT_VAR = 149
    CMD_ENABLE_CONTACT_HOST_NOTIFICATIONS = 150
    CMD_DISABLE_CONTACT_HOST_NOTIFICATIONS = 151
    CMD_ENABLE_CONTACT_SVC_NOTIFICATIONS = 152
    CMD_DISABLE_CONTACT_SVC_NOTIFICATIONS = 153
    CMD_ENABLE_CONTACTGROUP_HOST_NOTIFICATIONS = 154
    CMD_DISABLE_CONTACTGROUP_HOST_NOTIFICATIONS = 155
    CMD_ENABLE_CONTACTGROUP_SVC_NOTIFICATIONS = 156
    CMD_DISABLE_CONTACTGROUP_SVC_NOTIFICATIONS = 157
    CMD_CHANGE_RETRY_HOST_CHECK_INTERVAL = 158
    CMD_SEND_CUSTOM_HOST_NOTIFICATION = 159
    CMD_SEND_CUSTOM_SVC_NOTIFICATION = 160
    CMD_CHANGE_HOST_NOTIFICATION_TIMEPERIOD = 161
    CMD_CHANGE_SVC_NOTIFICATION_TIMEPERIOD = 162
    CMD_CHANGE_CONTACT_HOST_NOTIFICATION_TIMEPERIOD = 163
    CMD_CHANGE_CONTACT_SVC_NOTIFICATION_TIMEPERIOD = 164
    CMD_CHANGE_HOST_MODATTR = 165
    CMD_CHANGE_SVC_MODATTR = 166
    CMD_CHANGE_CONTACT_MODATTR = 167
    CMD_CHANGE_CONTACT_MODHATTR = 168
    CMD_CHANGE_CONTACT_MODSATTR = 169
    CMD_DEL_DOWNTIME_BY_HOST_NAME = 170
    CMD_DEL_DOWNTIME_BY_HOSTGROUP_NAME = 171
    CMD_DEL_DOWNTIME_BY_START_TIME_COMMENT = 172
    CMD_CUSTOM_COMMAND = 999
    _time_fmt = '%m-%d-%Y %T'

    # }}}
    # {{{ __init__(self, hostname, userid = None, password = None, 

    def __init__(self, hostname, userid = None, password = None, 
                 secure = None, cgi = '/nagios/cgi-bin/cmd.cgi'):
        parts = ['http',]
        if secure: parts.append('s')
        parts.append('://')
        parts.append(hostname)
        parts.append(cgi)
        self.uri = ''.join(parts)
        self.author = userid
        auth_manager = urllib2.HTTPPasswordMgrWithDefaultRealm()
        auth_manager.add_password(realm=None,
                          uri=self.uri,
                          user=userid,
                          passwd=password)
        auth_handler = urllib2.HTTPBasicAuthHandler(auth_manager)
        self.opener = urllib2.build_opener(auth_handler)
        self.opener.addheaders = [('User-agent', 'NagCGI Python Library/0.1')]
        return

# }}}
    # {{{ _dispatch(self, cmd, hostname, **kwargs):

    def _dispatch(self, cmd, **kwargs):
        '''Easily abused work-horse.

        Send the completed command to the Nagios server.  No checking.'''
        if kwargs.has_key('author'):
            if kwargs['author'] == None: kwargs['author'] = self.author
        kwargs['cmd_typ'] = cmd
        kwargs['cmd_mod'] = self._commit
        data = urllib.urlencode(kwargs)
        print "DIV data info: ", data
        return self.opener.open(self.uri, data).read()

    # }}}

    def _default_start_time(self):
        return time.strftime(self._time_fmt)
    
    def _default_end_time(self):
        return time.strftime(self._time_fmt, time.localtime(time.time() + 7200))
    
    def add_host_comment(self, hostname, comment, persistent = 1, author = None):
        return self._dispatch(self.CMD_ADD_HOST_COMMENT, host = hostname, 
                              com_author = author, com_data = comment, 
                              persistent = str(persistent))

    def ack_host_problem(self, hostname, comment, sticky_ack = 1, author = None):
        return self._dispatch(self.CMD_ACKNOWLEDGE_HOST_PROBLEM, host = hostname, 
                              com_author = author, com_data = comment, sticky_ack = str(sticky_ack))
                    
    def add_svc_comment(self, hostname, service, comment, persistent = 1,
                        author = None):
        return self._dispatch(self.CMD_ADD_SVC_COMMENT, host = hostname, service = service,
                              com_author = author, com_data = comment, 
                              persistent = str(persistent))

    def ack_svc_problem(self, hostname, service, comment, sticky_ack = 1,
                        send_notification = 0, author = None):
        return self._dispatch(self.CMD_ACKNOWLEDGE_SVC_PROBLEM, host = hostname, service = service,
                              com_author = author, com_data = comment, sticky_ack = str(sticky_ack),
                              send_notification = str(send_notification))

    def disable_svc_check(self, hostname, service):
        return self._dispatch(self.CMD_DISABLE_SVC_CHECK, host = hostname, service = service )

    def enable_svc_check(self, hostname, service):
        return self._dispatch(self.CMD_ENABLE_SVC_CHECK, host = hostname, service = service )
                    
    def disable_svc_notifications(self, hostname, service):
        return self._dispatch(self.CMD_DISABLE_SVC_NOTIFICATIONS, host = hostname, service = service )

    def enable_svc_notifications(self, hostname, service):
        return self._dispatch(self.CMD_ENABLE_SVC_NOTIFICATIONS, host = hostname, service = service )

    def schedule_svc_downtime(self, hostname, service, comment, author = None, hours = 2,
                              fixed = 0, end_time = None, start_time = None):
        if not start_time: start_time = self._default_start_time()
        if not end_time: end_time = self._default_end_time()
        return self._dispatch(self.CMD_SCHEDULE_SVC_DOWNTIME, host = hostname, service = service,
                              com_author = author, com_data = comment, fixed = str(fixed),
                              hours = str(hours), start_time = start_time, end_time = end_time)
                    
    def disable_notifications(self):
        return self._dispatch(self.CMD_DISABLE_NOTIFICATIONS )

    def enable_notifications(self):
        return self._dispatch(self.CMD_ENABLE_NOTIFICATIONS )

    def start_service_checks(self):
        return self._dispatch(self.CMD_START_ACCEPTING_PASSIVE_SVC_CHECKS ) + self._dispatch(self.CMD_START_EXECUTING_SVC_CHECKS )

    def stop_service_checks(self):
        return self._dispatch(self.CMD_STOP_ACCEPTING_PASSIVE_SVC_CHECKS ) + self._dispatch(self.CMD_STOP_EXECUTING_SVC_CHECKS )

    def disable_host_svc_checks(self, hostname, ahas = 1):
        return self._dispatch(self.CMD_DISABLE_SVC_CHECK, host = hostname, ahas = str(ahas) )

    def enable_host_svc_checks(self, hostname):
        return self._dispatch(self.CMD_ENABLE_SVC_CHECK, host = hostname, ahas = str(ahas) )
                    
    def disable_host_svc_notifications(self, hostname, ahas = 1):
        return self._dispatch(self.CMD_DISABLE_HOST_SVC_NOTIFICATIONS, host = hostname, ahas = str(ahas) )

    def enable_host_svc_notifications(self, hostname, ahas = 1):
        return self._dispatch(self.CMD_ENABLE_HOST_SVC_NOTIFICATIONS, host = hostname, ahas = str(ahas) )
                    

