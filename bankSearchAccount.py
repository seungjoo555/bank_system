import oracledb

def view_accounts(user_id):
    # 오라클 데이터베이스 연결 정보 설정
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
                while True:
                    print("\n" + "="*50)
                    print("  [내 계좌 조회 메뉴]")
                    print("="*50)
                    print("1. 전체 계좌 조회")
                    print("2. 은행별 검색")
                    print("3. 계좌번호별 검색")
                    print("4. 별칭별 검색")
                    print("5. 이전 메뉴로")
                    
                    search_choice = input("검색 방식을 선택하세요: ")

                    # 기본 SQL 쿼리 (요구사항 2번: 은행명, 계좌번호, 계좌주명, 잔액, 별칭 포함)
                    # USERS, BANKS, ACCOUNTS 테이블을 조인하여 모든 정보를 가져옴
                    base_sql = """
                    SELECT B.BANK_NAME, A.ACCOUNT_NUM, U.USER_NAME, A.BALANCE, A.ALIAS
                    FROM ACCOUNTS A
                    JOIN BANKS B ON A.BANK_ID = B.BANK_ID
                    JOIN USERS U ON A.USER_ID = U.USER_ID
                    WHERE A.USER_ID = :1
                    """
                    
                    params = [user_id]

                    # 요구사항 8번 반영: 검색 조건 추가
                    if search_choice == '1':
                        pass # 전체 조회이므로 추가 조건 없음
                    elif search_choice == '2':
                        bank_name = input("검색할 은행명을 입력하세요: ")
                        base_sql += " AND B.BANK_NAME LIKE :2"
                        params.append(f"%{bank_name}%")
                    elif search_choice == '3':
                        acc_num = input("검색할 계좌번호를 입력하세요: ")
                        base_sql += " AND A.ACCOUNT_NUM LIKE :2"
                        params.append(f"%{acc_num}%")
                    elif search_choice == '4':
                        alias = input("검색할 별칭을 입력하세요: ")
                        base_sql += " AND A.ALIAS LIKE :2"
                        params.append(f"%{alias}%")
                    elif search_choice == '5':
                        return
                    else:
                        print("[오류] 잘못된 선택입니다.")
                        return

                    cursor.execute(base_sql, params)
                    rows = cursor.fetchall()

                    if not rows:
                        print("\n[알림] 등록된 계좌가 없거나 검색 결과가 없습니다.")
                    else:
                        print("\n" + "-"*80)
                        print(f"{'은행명':<10} | {'계좌번호':<18} | {'계좌주':<8} | {'잔액':>12} | {'별칭':<15}")
                        print("-"*80)
                        for bank, acc, owner, bal, alias in rows:
                            # 별칭이 없을 경우(None) 공백 처리
                            display_alias = alias if alias else "N/A"
                            print(f"{bank:<10} | {acc:<18} | {owner:<8} | {bal:>12,d}원 | {display_alias:<15}")
                        print("-"*80)

    except Exception as e:
        print(f"\n[시스템 에러] 조회 중 오류 발생: {e}")