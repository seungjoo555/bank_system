import oracledb

def withdraw_money(user_id):
    # 오라클 데이터베이스 연결 정보 설정
    conn_info = {
        "user": "c##bank",
        "password": "bank",
        "dsn": "localhost:1521/FREE"  # host:port/service_name
    }
    connection = None
    try:
        with oracledb.connect(
            user=conn_info["user"],
            password=conn_info["password"],
            dsn=conn_info["dsn"]
        ) as connection:
            with connection.cursor() as cursor:

                # 1. 사용자의 계좌 목록 조회 (요구사항 2번: 은행명, 계좌번호, 잔액, 별칭 포함) [1]
                sql_check = """
                SELECT A.ACCOUNT_NUM, B.BANK_NAME, A.BALANCE, A.ALIAS
                FROM ACCOUNTS A
                JOIN BANKS B ON A.BANK_ID = B.BANK_ID
                WHERE A.USER_ID = :1
                """
                cursor.execute(sql_check, [user_id])
                accounts = cursor.fetchall()

                # 2. 계좌 존재 여부 확인 [1]
                if not accounts:
                    print("\n[알림] 등록된 계좌가 없습니다. 먼저 계좌를 생성해 주세요.")
                    return

                # 3. 출금할 계좌 선택
                print("\n--- [출금할 계좌를 선택하세요] ---")
                for i, acc in enumerate(accounts, 1):
                    # acc[0]: 계좌번호, acc[1]: 은행명, acc[2]: 잔액, acc[3]: 별칭
                    alias_display = f"({acc[3]})" if acc[3] else ""
                    print(f"{i}. {acc[0]} | {acc[1]} | 잔액: {acc[2]:,d}원 {alias_display}")
                
                try:
                    choice = int(input("\n선택 (번호 입력): ")) - 1
                    if not (0 <= choice < len(accounts)):
                        print("[오류] 잘못된 번호 선택입니다.")
                        return
                except ValueError:
                    print("[오류] 숫자만 입력 가능합니다.")
                    return

                selected_acc_num = accounts[choice][0]
                current_balance = accounts[choice][2]
                    
                # 4. 출금 금액 입력 및 검증
                amount = int(input("출금할 금액을 입력하세요: "))
                
                if amount <= 0:
                    print("[오류] 0원 이하의 금액은 출금할 수 없습니다.")
                    return
                    
                # 잔액 확인 (요구사항 11번 원칙 적용: 이체금액/출금액이 잔액보다 많은 경우 취소) [1]
                if amount > current_balance:
                    print(f"[오류] 잔액이 부족합니다. (현재 잔액: {current_balance:,d}원)")
                    return

                # 5. DB 업데이트 (잔액 감액 및 거래 내역 기록)
                # 계좌 잔액 업데이트
                sql_update = "UPDATE ACCOUNTS SET BALANCE = BALANCE - :1 WHERE ACCOUNT_NUM = :2"
                cursor.execute(sql_update, [amount, selected_acc_num])

                # 거래 내역 기록 (TRANSACTIONS 테이블)
                sql_trans = """
                INSERT INTO TRANSACTIONS (TRANS_ID, FROM_ACCOUNT, AMOUNT, TRANS_TYPE)
                VALUES (SEQ_TRANS_ID.NEXTVAL, :1, :2, '출금')
                """
                cursor.execute(sql_trans, [selected_acc_num, amount])

                # 6. 트랜잭션 확정 (요구사항 13번: 문제가 없을 경우에만 반영) [2]
                connection.commit()
                print(f"\n[성공] {selected_acc_num} 계좌에서 {amount:,d}원이 출금되었습니다.")
                print(f"남은 잔액: {current_balance - amount:,d}원")

    except Exception as e:
        if connection:
            connection.rollback() # 오류 시 모든 작업 취소 (요구사항 13번 준수) [2]
        print(f"\n[시스템 에러] 출금 처리 중 오류 발생: {e}")