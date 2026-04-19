import oracledb

def transfer(user_id):
    conn_info = {
        "user": "c##bank",
        "password": "bank",
        "dsn": "localhost:1521/FREE"  # host:port/service_name
    }
    connection = None
    with oracledb.connect(
        user=conn_info["user"],
        password=conn_info["password"],
        dsn=conn_info["dsn"]
    ) as connection:
        with connection.cursor() as cursor:
            try:
                # 1. 내 계좌 목록 조회 및 유무 확인
                # 계좌 정보는 은행명, 계좌번호, 계좌주명, 잔액, 별칭으로 구성됨 [1]
                sql_my_accs = """
                SELECT A.ACCOUNT_NUM, B.BANK_NAME, A.BALANCE, A.ALIAS, U.USER_NAME
                FROM ACCOUNTS A
                JOIN BANKS B ON A.BANK_ID = B.BANK_ID
                JOIN USERS U ON A.USER_ID = U.USER_ID
                WHERE A.USER_ID = :1
                """
                cursor.execute(sql_my_accs, [user_id])
                my_accounts = cursor.fetchall()

                if not my_accounts:
                    print("\n[알림] 등록된 계좌가 없습니다. 먼저 계좌를 생성해 주세요.") # 요구사항 반영
                    return

                # 2. 출금할 내 계좌 선택
                print("\n--- [이체에 사용할 내 계좌 선택] ---")
                for i, acc in enumerate(my_accounts, 1):
                    # acc[0]:계좌번호, acc[1]:은행명, acc[2]:잔액, acc[3]:별칭
                    alias_str = f"({acc[3]})" if acc[3] else ""
                    print(f"{i}. {acc[0]} {acc[1]} | 잔액: {acc[2]:,d}원 {alias_str}")
                
                from_choice = int(input("\n출금 계좌 번호 선택: ")) - 1
                from_acc_num = my_accounts[from_choice][0]
                my_balance = my_accounts[from_choice][2]

                # 3. 이체 방식 선택
                print("\n--- [이체 방식 선택] ---")
                print("1. 상대방 계좌번호 직접 입력")
                print("2. 상대방 아이디로 계좌 검색")
                method = input("방식을 선택하세요: ")

                to_acc_num = None

                if method == '1':
                    to_acc_num = input("상대방 계좌번호를 입력하세요: ")
                    # 계좌 존재 확인
                    cursor.execute("SELECT COUNT(*) FROM ACCOUNTS WHERE ACCOUNT_NUM = :1", [to_acc_num])
                    a = cursor.fetchone()
                    if a[0] == 0:
                        print("[오류] 존재하지 않는 계좌번호입니다.")
                        return

                elif method == '2':
                    target_id = input("상대방 아이디를 입력하세요: ")
                    # 해당 아이디의 계좌 목록 조회 [1]
                    sql_target_accs = """
                    SELECT A.ACCOUNT_NUM, B.BANK_NAME, U.USER_NAME
                    FROM ACCOUNTS A
                    JOIN BANKS B ON A.BANK_ID = B.BANK_ID
                    JOIN USERS U ON A.USER_ID = U.USER_ID
                    WHERE A.USER_ID = :1
                    """
                    cursor.execute(sql_target_accs, [target_id])
                    target_accounts = cursor.fetchall()

                    if not target_accounts:
                        print(f"[알림] 해당 아이디({target_id})로 등록된 계좌가 없습니다.")
                        return
                    
                    print(f"\n--- [{target_id}]님의 계좌 목록 ---")
                    for i, acc in enumerate(target_accounts, 1):
                        print(f"{i}. (계좌번호: {acc[0]}) (은행 : {acc[1]}) | 예금주: {acc[2]}")
                    
                    to_choice = int(input("이체할 계좌 번호를 선택하세요: ")) - 1
                    to_acc_num = target_accounts[to_choice][0]

                # 4. 금액 입력 및 검증
                amount = int(input("이체할 금액을 입력하세요: "))

                # 요구사항 10번: 0원 초과 금액만 가능 [1]
                if amount <= 0:
                    print("[오류] 이체 금액은 0원을 초과해야 합니다.")
                    return

                # 요구사항 11번: 이체 금액이 잔액보다 많은 경우 취소 [1]
                # (소스상 '적은 경우'로 기재되어 있으나 논리적 잔액 검증으로 구현)
                if amount > my_balance:
                    print(f"[오류] 잔액이 부족하여 이체가 취소됩니다. (현재 잔액: {my_balance:,d}원)")
                    return

                # 5. 이체 작업 수행 (트랜잭션)
                # 내 계좌 출금
                cursor.execute("UPDATE ACCOUNTS SET BALANCE = BALANCE - :1 WHERE ACCOUNT_NUM = :2", [amount, from_acc_num])
                # 상대방 계좌 입금
                cursor.execute("UPDATE ACCOUNTS SET BALANCE = BALANCE + :1 WHERE ACCOUNT_NUM = :2", [amount, to_acc_num])
                
                # 거래 내역 기록
                sql_trans = """
                INSERT INTO TRANSACTIONS (TRANS_ID, FROM_ACCOUNT, TO_ACCOUNT, AMOUNT, TRANS_TYPE)
                VALUES (SEQ_TRANS_ID.NEXTVAL, :1, :2, :3, '계좌이체')
                """
                cursor.execute(sql_trans, [from_acc_num, to_acc_num, amount])

                # 6. 최종 확정 (요구사항 13번: 문제 발생 시 롤백, 성공 시 커밋) [2]
                connection.commit()
                print(f"\n[성공] {to_acc_num} 계좌로 {amount:,d}원 이체가 완료되었습니다.")

            except Exception as e:
                if connection:
                    connection.rollback() # 요구사항 13번 반영: 모든 작업 취소 [2]
                print(f"\n[시스템 에러] 이체 중 문제가 발생하여 모든 작업이 취소되었습니다: {e}")


def transfer_db(user_id):
    """
    다른 DB와 연동하여 상대방 정보를 조회하고 이체하는 기능
    """
    local_conn = None
    remote_conn = None
    
    # DB 연결 정보 (구조는 동일하다고 가정)
    local_info = {"user": "c##bank", "password": "bank", "dsn": "localhost:1521/FREE"}
    remote_info = {"user": "c##bank", "password": "bank", "dsn": "172.31.57.146:1521/FREE"}

    try:
        # 1. 로컬 및 외부 DB 연결
        local_conn = oracledb.connect(**local_info)
        remote_conn = oracledb.connect(**remote_info)
        
        local_cur = local_conn.cursor()
        remote_cur = remote_conn.cursor()

        # 동기화 작업
        local_cur.execute("""
            SELECT * FROM USERS
        """)
        check_user = local_cur.fetchall()
        remote_cur.execute("""
            SELECT * FROM USERS
        """)
        check_user2 = remote_cur.fetchall()
        for user in check_user2:
            if user[0] not in (us[0] for us in check_user):
                local_cur.execute("""
                    insert into users values(:1, :2, :3, :4)
                """, [user[0], '123', user[2], "USER"])

        local_cur.execute("""
            SELECT * FROM ACCOUNTS
        """)
        check_account = local_cur.fetchall()
        remote_cur.execute("""
            SELECT * FROM ACCOUNTS
        """)
        check_account2 = remote_cur.fetchall()
        for acc in check_account2:
            if acc[0] not in (ac[0] for ac in check_account):
                local_cur.execute("""
                    insert into ACCOUNTS values(:1, :2, :3, :4, :5)
                """, [acc[0], 1, acc[1], acc[3], acc[4]])

        local_conn.commit() # 동기화 커밋

        # 2. 내 계좌 선택 (로컬 DB)
        local_cur.execute("""
            SELECT A.ACCOUNT_NUM, B.BANK_NAME, A.BALANCE 
            FROM ACCOUNTS A JOIN BANKS B ON A.BANK_ID = B.BANK_ID 
            WHERE A.USER_ID = :1
        """, [user_id])
        my_accs = local_cur.fetchall()
        
        if not my_accs:
            print("\n[알림] 내 계좌가 없습니다.")
            return

        print("\n--- [1. 출금할 내 계좌 선택] ---")
        for i, acc in enumerate(my_accs, 1):
            print(f"{i}. {acc[0]} | {acc[1]} | 잔액: {acc[2]:,d}원")
        from_choice = int(input("선택: ")) - 1
        from_acc = my_accs[from_choice][0]
        my_balance = my_accs[from_choice][2]

        # 3. 상대방 아이디 목록 조회 (외부 DB)
        print("\n--- [2. 이체 상대방(ID) 선택 - 외부 DB 조회] ---")
        remote_cur.execute("SELECT USER_ID, NAME FROM USERS WHERE ROLE != 'admin' ORDER BY USER_ID")
        remote_users = remote_cur.fetchall()

        for i, user in enumerate(remote_users, 1):
            print(f"{i}. 아이디: {user[0]} (성함: {user[1]})")
        user_choice = int(input("상대방 선택: ")) - 1
        target_id = remote_users[user_choice][0]

        # 4. 선택한 아이디의 계좌 목록 조회 (외부 DB) [1]
        print(f"\n--- [3. {target_id}님의 입금 계좌 선택] ---")
        remote_cur.execute("""
            SELECT A.ACCOUNT_NUMBER, B.BANK_NAME 
            FROM ACCOUNTS A JOIN BANK B ON A.BANKID = B.BANK_NAME 
            WHERE A.USERID = :1
        """, [target_id])
        target_accs = remote_cur.fetchall()

        if not target_accs:
            print("[오류] 해당 사용자는 등록된 계좌가 없습니다.")
            return

        for i, acc in enumerate(target_accs, 1):
            print(f"{i}. {acc[0]} | {acc[1]}")
        while True:
            to_choice = int(input("입금 계좌 선택: ")) - 1
            to_acc = target_accs[to_choice][0]
            if to_choice < 0 or to_choice > len(target_accs):
                print("숫자를 다시 입력해 주세요")
                continue
            else:
                break

        # 5. 이체 금액 입력 및 검증 [1]
        amount = int(input("\n이체할 금액을 입력하세요: "))
        
        if amount <= 0: # 요구사항 10번 반영
            print("[오류] 이체 금액은 0원을 초과해야 합니다. [1]")
            return
        if amount > my_balance: # 요구사항 11번 반영
            print(f"[오류] 잔액이 부족하여 취소됩니다. (잔액: {my_balance:,d}원) [1]")
            return
        
        # 6. 이체 실행 (분산 트랜잭션 시뮬레이션) [2]
        try:
            # 로컬 DB 출금
            local_cur.execute("UPDATE ACCOUNTS SET BALANCE = BALANCE - :1 WHERE ACCOUNT_NUM = :2", [amount, from_acc])
            # 외부 DB 입금
            remote_cur.execute("UPDATE ACCOUNTS SET BALANCE = BALANCE + :1 WHERE ACCOUNT_NUMBER = :2", [amount, to_acc])
            print(1)
            # 거래 내역 기록 (로컬) [1]
            local_cur.execute("""
                INSERT INTO TRANSACTIONS (TRANS_ID, FROM_ACCOUNT, TO_ACCOUNT, AMOUNT, TRANS_TYPE)
                VALUES (SEQ_TRANS_ID.NEXTVAL, :1, :2, :3, '타행이체')
            """, [from_acc, to_acc, amount])
            print(2)
            # 거래 내역 기록 (외부)
            remote_cur.execute("""
                INSERT INTO LOG (LOG_ID, USERID, ACCOUNT_NUMBER, LOG_TYPE, LOG_MONEY, LOG_DATE)
                VALUES (log_no.NEXTVAL, :1, :2, :3, :4, sysdate)
            """, [target_id, to_acc, '이체당함 <- '+ from_acc, amount])
            print(3)

            # 양쪽 모두 커밋
            local_conn.commit()
            remote_conn.commit()
            print(f"\n[성공] {target_id}님({to_acc})에게 {amount:,d}원 이체가 완료되었습니다.")

        except Exception as e:
            # 요구사항 13번 반영: 문제 발생 시 모든 작업 취소 [2]
            local_conn.rollback()
            remote_conn.rollback()
            print(f"\n[시스템 에러] 이체 작업 중 오류가 발생하여 모든 작업이 취소되었습니다: {e} [2]")

    except Exception as e:
        print(f"\n[연결 에러] DB 접속 중 오류 발생: {e}")

    finally:
        if local_conn: local_conn.close()
        if remote_conn: remote_conn.close()