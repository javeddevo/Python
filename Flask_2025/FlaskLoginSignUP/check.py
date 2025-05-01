import jwt

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImtvcEBleGFtcGxlLmNvbSIsImV4cCI6MTc0NTcwMjk1MH0.2LF-COfT9-Zp_j22UZAmHr_QX3tnuSDcyLyQ0sBu9H8"
decoded_token = jwt.decode(token, options={"verify_signature": False})
print(decoded_token)
