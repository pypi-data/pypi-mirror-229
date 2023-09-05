# Updates the Dynamic DNS (DDNS) record for a given subdomain and domain using the Dynu API

## Tested against Windows 10 / Python 3.10 / Anaconda

## pip install dynuipv4update

```python
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
```