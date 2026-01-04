from src.infrastructure.security.pw_hasher import PasswordHasher


def test_pw_hasher():
    pw_hasher = PasswordHasher()

    my_pw = "pw123"
    hashed_pw = pw_hasher.hash_password(my_pw)

    # Ensure hashing works
    assert my_pw != hashed_pw
    # Ensure verifying hashed pw works
    assert pw_hasher.verify_password(my_pw, hashed_pw) is True

