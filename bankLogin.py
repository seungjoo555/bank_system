import oracledb
import getpass

def login_user():
    # 1. 오라클 데이터베이스 연결 정보 설정
    conn_info = {
        "user": "c##bank",
        "password": "bank",
        "dsn": "localhost:1521/FREE"  # host:port/service_name
    }

    connection = None
    try:
        # 2. DB 연결
        with oracledb.connect(
            user=conn_info["user"],
            password=conn_info["password"],
            dsn=conn_info["dsn"]
        ) as connection:
            with connection.cursor() as cursor:
                # 3. 사용자로부터 정보 입력 받기
                user_id = input("아이디를 입력하세요: ")
                password = getpass.getpass("비밀번호를 입력하세요: ")

                # 4. SQL 실행
                sql = """
                SELECT USER_ID, PASSWORD, USER_NAME, ROLE
                FROM USERS
                WHERE USER_ID = :1 and PASSWORD = :2
                """
                
                user_info = list(cursor.execute(sql, (user_id, password)))
                if user_info:
                    print()
                    print(f"{'*' * 10}{user_info[0][0]}님 로그인 되었습니다.{'*' * 10}")
                    return True, user_info[0][0], user_info[0][2], user_info[0][3]
                else:
                    print("아이디가 없거나 비밀번호가 틀렸습니다.")
                    return False, None
                
    except Exception as e:
        print(f"\n[오류] 로그인 중 문제가 발생했습니다: {e}")