import hashlib
import json
import sys
from collections import defaultdict, deque

import kthread
import kthread_sleep
import requests
from getpublicipv4 import get_ip_of_this_pc
from pfehler import pfehler
ipconfig = sys.modules[__name__]
ipconfig.allipscans = defaultdict(lambda: deque([], 5))


def update_dynamic_dns(
    apikey,
    subdomain,
    domain,
    password,
    as_thread=True,
    frequency=30,
    print_update=True,
):
    r"""
    Update the Dynamic DNS (DDNS) record for a given subdomain and domain using the Dynu API ( https://www.dynu.com/ ).

    This function sends a request to the Dynu API to update the IP (v4 only!!) address associated with
    the specified subdomain and domain using the provided credentials. It can be used as a
    one-time call or as a background thread that periodically updates the IP address.

    Args:
        apikey (str): The API key for authentication with the Dynu API.
        subdomain (str): The subdomain to update (e.g., 'bububaba' in 'bububaba.ddnsfree.com').
        domain (str): The domain to update (e.g., 'ddnsfree.com').
        password (str): The password for authentication with Dynu, used to generate a password hash.
        as_thread (bool, optional): If True, run the update as a background thread. Default is True.
        frequency (int, optional): The frequency (in seconds) at which to update the IP address.
            Ignored if as_thread is False. Default is 30 seconds.
        print_update (bool, optional): If True, print updates when the IP address is changed.
            Ignored if as_thread is False. Default is True.

    Returns:
        If as_thread is True, returns a thread object representing the background update task.
        If as_thread is False, returns the current IP address for the specified subdomain and domain.

    Example:
        subdomain = r"bababu"
        domain = "ddnsfree.com"
        apikey = "xxxxxx"
        sleep_ip_update = 30
        dyn_password = r"xxxxx"


        # one time call
        updatedip = update_dynamic_dns(
            apikey=apikey,
            subdomain=second_level_domain,
            domain=top_level_domain,
            password=dyn_password,
            as_thread=False,
            frequency=30,
            print_update=True,
        )
        print(updatedip)


        # as thread
        update_dynamic_dns(
            apikey=apikey,
            subdomain=second_level_domain,
            domain=top_level_domain,
            password=dyn_password,
            as_thread=True,
            frequency=30,
            print_update=True,
        )
        print(
            ipconfig.allipscans[f"{second_level_domain}.{top_level_domain}"]
        )  # ips are stored here when you use as_thread=True

    """

    def _update_ip():
        while True:
            try:
                passwordhash = hashlib.md5(password.encode("utf-8")).hexdigest()
                myipnow = get_ip_of_this_pc()
                linkx = f"http://api.dynu.com/nic/update?hostname={subdomain}.{domain}&myip={myipnow}&myipv6=no&password={passwordhash}"

                with requests.get(linkx) as fax:
                    pass
                with requests.get(
                    "https://api.dynu.com/v2/dns",
                    headers={"accept": "application/json", "API-Key": apikey},
                ) as rea:
                    (rea) = rea.content
                resdax = [
                    (x[1][0]["unicodeName"], x[1][0]["ipv4Address"])
                    for x in json.loads(rea).items()
                    if x[0] == "domains"
                ][0]
                if resdax[-1] != myipnow:
                    kthread_sleep.sleep(frequency)
                    continue
                if not as_thread:
                    return myipnow
                ipconfig.allipscans[f"{subdomain}.{domain}"].append(myipnow)
                if print_update:
                    print(f"{subdomain}.{domain} - IP: {myipnow}")
            except Exception:
                pfehler()
            kthread_sleep.sleep(frequency)

    if as_thread:
        t = kthread.KThread(target=_update_ip)
        t.daemon = True
        t.start()
        return t
    return _update_ip()


