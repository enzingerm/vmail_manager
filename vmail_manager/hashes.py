import crypt

SHA512_PRE = "{SHA512-CRYPT}"

def check_pw(password, crypted):
    if crypted.startswith(f"{SHA512_PRE}$6$"):
        without_scheme = crypted.removeprefix(f"{SHA512_PRE}$6$")
        salt, hash = without_scheme.split("$")
        computed = crypt.crypt(password, f"$6${salt}")
        return SHA512_PRE + computed == crypted
    raise Exception("Hash algorithm not supported!")

def create_hash(password):
    salt = crypt.mksalt(crypt.METHOD_SHA512)
    return SHA512_PRE + crypt.crypt(password, salt)
