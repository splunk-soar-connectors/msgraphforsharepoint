**Unreleased**

* Percent-encode the asset name when building the OAuth redirect URI and admin consent URL, so asset names containing spaces or other special characters no longer produce a redirect URI that Azure AD rejects (AADSTS50011).
