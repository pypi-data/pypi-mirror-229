import urllib3.request
import urllib.parse
import json
import certifi

class AuthContext:
    """
    The AuthContext class is used to contain data about the user or client app that
    will be used to identify the program or user that is making calls to the server
    to get data or make updates.

    Any authorized calls as made from the python api expect an instance of an
    AuthContext class as a parameter.

    If you are creating an AuthContext class for a user you must call get_token
    to authorize the user id and password combination prior to making any calls.

    If you are creating an AuthContext for a client app, you must register
    that client app with the server and obtain a client_id and client token,
    you do not need to call get_token for client type AuthContext instances.
    """
    @classmethod
    def for_user(cls, appid, uid, pwd, url="https://api.nuviot.com"):
        """
        Creates an authorization context for a user with an user id and password

        Parameters
        ----------
        appid:
            Unique application id that will be sent along with the user login

        uid: 
            User Id, which is usually the email address for the user

        pwd:
            Password for the user

        url:
            Optional, url to login the account, unless this is a custom installation, the default will be https://api.nuviot.com
        """

        cls.auth_type = 'user'
        cls.appid = appid
        cls.uid = uid
        cls.pwd = pwd
        cls.url = url
        cls.auth_token = ''
        cls.auth_token_expires = ''
        cls.refresh_token = ''
        cls.refresh_expires = ''
        cls.auth_expires = ''
        cls.app_instance_id = ''
        return cls()
    
    @classmethod
    def for_client_app(cls, clientid, client_token, url="https://api.nuviot.com"):
        """
        Creates an authorization context for client id and client token as registered on NuvIoT

        Parameters
        ----------
        appid:
            Unique application id that will be sent along with the user login

        uid: 
            User Id, which is usually the email address for the user

        pwd:
            Password for the user

        url:
            Optional, url to login the account, unless this is a custom installation, the default will be https://api.nuviot.com
        """

        cls.auth_type = 'clientapp'
        cls.client_id = clientid
        cls.url = url
        cls.client_token = client_token
        return cls()
        
    def get_token(self):
        """
        Make an authentication call to the server to generate an authorization token
        this only applies for user type logins.

        When this method is ran the auth token and refresh token are stored in the 
        AuthContext class, so the the AuthContext class can be passed in to methods
        required to make authorized calls. 
        """
        if self.auth_type == 'user':
            post = {"grantType": "password",
              "appId": self.appid,
              "deviceId": "0000000000000000000000000000",
              "appInstanceId": "0000000000000000000000000000",
              "clientType": "aiclient",
              "email": self.uid,
              "userName": self.uid,
              "password": self.pwd,
              "refreshToken": None,
              "orgId": None,
              "orgName": None
            }

            data = json.dumps(post)

            http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
            headers={'Content-Type': 'application/json'}
            client_auth_uri = "%s/api/v1/auth" % self.url
            print(client_auth_uri)
            r = http.request("POST",client_auth_uri, body=data, headers=headers, preload_content=False)

            responseJSON = ''
            for chunk in r.stream(32):
                responseJSON += chunk.decode("utf-8")

            r.release_conn()
            print("REQUESTED AUTH")
            print(responseJSON)
            ro = json.loads(responseJSON)

            self.app_instance_id = ro["result"]["appInstanceId"]
            self.auth_token_expires = ro["result"]["accessTokenExpiresUTC"]
            self.refresh_expires = ro["result"]["refreshTokenExpiresUTC"]
            self.auth_token = ro["result"]["accessToken"]
            self.refresh_token = ro["result"]["refreshToken"]
        return
