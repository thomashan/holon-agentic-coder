Whilst `mitmproxy` is running in the background

```
HTTP_PROXY=http://localhost:8080 HTTPS_PROXY=http://localhost:8080 NODE_EXTRA_CA_CERTS=$HOME/.mitmproxy/mitmproxy-ca-cert.cer claude --settings $HOME/.claude/lmstudio.settings.json
```
