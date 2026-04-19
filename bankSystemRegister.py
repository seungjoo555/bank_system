import oracledb
import getpass

def register_user():
    # 1. 오라클 데이터베이스 연결 정보 설정
    # (본인의 DB 환경에 맞게 수정하세요)
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

                print("=== 회원가입 ===")
                # 3. 사용자로부터 정보 입력 받기
                while True:
                    user_id = input("사용할 아이디를 입력하세요(영문자): ")
                    if len(user_id) > 20:
                        print("아이디는 20자를 넘을 수 없습니다.")
                        continue
                    password = getpass.getpass("비밀번호를 입력하세요: ")
                    if len(password) > 100:
                        print("비밀번호는 100자를 넘을 수 없습니다.")
                        continue
                    user_name = input("성함(계좌주명)을 입력하세요: ") # 요구사항 2번 반영
                    break

                # 4. SQL 실행 (기본 권한은 'USER'로 설정)
                sql = """
                INSERT INTO USERS (USER_ID, PASSWORD, USER_NAME, ROLE)
                VALUES (:1, :2, :3, 'USER')
                """
                
                cursor.execute(sql, (user_id, password, user_name))
                
                # 5. 트랜잭션 확정 (Commit)
                connection.commit()
                print(f"\n[알림] {user_name}님, 회원가입이 완료되었습니다!")
                print("이제 메인 메뉴에서 로그인을 진행해 주세요.")

    except oracledb.IntegrityError:
        print("\n[오류] 이미 존재하는 아이디입니다. 다른 아이디를 사용해 주세요.")
    except Exception as e:
        print(f"\n[오류] 회원가입 중 문제가 발생했습니다: {e}")