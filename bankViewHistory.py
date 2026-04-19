import oracledb

def view_all_history(user_id):
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

                # 1. 사용자의 모든 계좌 정보 가져오기 (요구사항 2, 7번 반영)
                sql_accounts = """
                SELECT A.ACCOUNT_NUM, B.BANK_NAME, A.ALIAS, A.BALANCE
                FROM ACCOUNTS A
                JOIN BANKS B ON A.BANK_ID = B.BANK_ID
                WHERE A.USER_ID = :1
                ORDER BY A.ACCOUNT_NUM
                """
                cursor.execute(sql_accounts, [user_id])
                my_accounts = cursor.fetchall()

                if not my_accounts:
                    print("\n[알림] 등록된 계좌가 없습니다.")
                    return

                print(f"\n{'='*35}")
                print(f"  [{user_id}]님의 통합 거래내역")
                print(f"{'='*35}")

                # 2. 각 계좌별로 거래 내역 조회 (요구사항 9번: 입금, 출금, 이체 포함)
                for acc_num, bank_name, alias, balance in my_accounts:
                    alias_display = f"({alias})" if alias else ""
                    print(f"\n▶ 계좌: {acc_num} | {bank_name} {alias_display}")
                    print(f"   현재 잔액: {balance:,d}원")
                    print("-" * 85)
                    print(f"{'거래일시':<20} | {'유형':<10} | {'상대방/출처':<18} | {'금액':>12}")
                    print("-" * 85)

                    # 해당 계좌의 상세 거래 내역 쿼리
                    sql_history = """
                    SELECT TRANS_TYPE, FROM_ACCOUNT, TO_ACCOUNT, AMOUNT, 
                        TO_CHAR(TRANS_DATE, 'YYYY-MM-DD HH24:MI:SS') AS T_DATE
                    FROM TRANSACTIONS
                    WHERE FROM_ACCOUNT = :acc_num OR TO_ACCOUNT = :acc_num
                    ORDER BY TRANS_DATE DESC
                    """
                    cursor.execute(sql_history, {'acc_num': acc_num})
                    history = cursor.fetchall()

                    if not history:
                        print("   (거래 내역이 없습니다.)")
                    else:
                        for ttype, f_acc, t_acc, amt, tdate in history:
                            display_acc = ""
                            if ttype == '입금':
                                display_acc = "본인입금"
                                display_amt = f"+{amt:,d}"
                            elif ttype == '출금':
                                display_acc = "본인출금"
                                display_amt = f"-{amt:,d}"
                            elif ttype == '계좌이체':
                                if f_acc == acc_num: # 해당 계좌에서 나간 경우
                                    display_acc = f"To: {t_acc}"
                                    display_amt = f"-{amt:,d}"
                                else: # 해당 계좌로 들어온 경우
                                    display_acc = f"From: {f_acc}"
                                    display_amt = f"+{amt:,d}"
                            else:
                                display_acc = "기타"
                                display_amt = f"{amt:,d}"

                            print(f"{tdate:<20} | {ttype:<10} | {display_acc:<18} | {display_amt:>12}원")
                    print("-" * 85)

    except Exception as e:
        print(f"\n[시스템 에러] 조회 중 오류 발생: {e}")