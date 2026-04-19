import oracledb
import random

def create_account(user_id):
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
                num = ['0','1','2','3','4','5','6','7','8','9']

                # 1. 은행 선택
                while True:
                    print("계좌를 만들 은행을 선택 하세요.")
                    print("1.하나 2.우리 3.국민 4.신한 5.기업")
                    bank_id = int(input("번호를 선택해주세요. : "))
                    if 0 > bank_id and bank_id > 5:
                        print("숫자를 다시 입력하세요.")
                    else:
                        break

                # 2. 계좌번호 자동 생성 있는 계좌인지 확인
                sql = """
                SELECT ACCOUNT_NUM
                FROM ACCOUNTS
                """
                cursor.execute(sql)
                check_account = []
                for row in cursor:
                    check_account.append(row[0])
                while True:
                    account_num = (''.join(random.choices(num, k=3)))+'-'+(''.join(random.choices(num, k=3)))+'-'+(''.join(random.choices(num, k=6)))
                    #계좌가 없으면 생성하고 아니면 다시 조합
                    if check_account.count(account_num) == 0:
                        break

                alias = input("계좌 별칭을 입력하세요 (선택사항): ")

                # 3. 최초 입금액 검증 (요구사항 12번 반영)
                while True:
                    try:
                        initial_deposit = int(input("최초 입금액을 입력하세요 (1,000원 이상): "))
                        if initial_deposit >= 1000:
                            break
                        else:
                            print("[오류] 최초 생성 시 1,000원 이상 입금해야 합니다.")
                    except ValueError:
                        print("[오류] 숫자만 입력 가능합니다.")

                # 4. ACCOUNTS 테이블에 계좌 정보 저장
                # 계좌주명은 USERS 테이블과 조인하여 가져오거나 로직상 처리
                sql_account = """
                INSERT INTO ACCOUNTS (ACCOUNT_NUM, BANK_ID, USER_ID, BALANCE, ALIAS)
                VALUES (:1, :2, :3, :4, :5)
                """
                cursor.execute(sql_account, (account_num, bank_id, user_id, initial_deposit, alias))

                # 5. 최초 입금 내역을 TRANSACTIONS 테이블에 기록 (선택 사항이나 권장함)
                sql_trans = """
                INSERT INTO TRANSACTIONS (TRANS_ID, TO_ACCOUNT, AMOUNT, TRANS_TYPE)
                VALUES (SEQ_TRANS_ID.NEXTVAL, :1, :2, '입금(개설)')
                """
                cursor.execute(sql_trans, (account_num, initial_deposit))

                connection.commit()
                print(f"[알림] 생성된 계좌번호: {account_num}")
                print(f"\n[성공] {account_num} 계좌가 정상적으로 생성되었습니다.")
                
    except Exception as e:
        print(f"\n[시스템 에러] 계좌 생성 중 오류 발생: {e}")