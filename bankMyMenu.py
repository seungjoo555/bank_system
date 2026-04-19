import oracledb
import random

def manage_my_accounts(user_id):
    """3. 내 계좌 관리 서브 메뉴"""
    while True:
        print("\n" + "-"*20)
        print("  내 계좌 관리")
        print("-"*20)
        print("1. 내 계좌 등록")
        print("2. 내 계좌 수정 (별칭 변경)")
        print("3. 내 계좌 삭제")
        print("4. 이전 메뉴로")
        print("-"*20)

        sub_choice = input("번호 선택: ")

        if sub_choice == '1':
            # 요구사항 3번에 따라 제공되는 은행에 한해 등록 [1]
            register_account(user_id)
        elif sub_choice == '2':
            # 요구사항 4번에 따라 별칭 수정 기능 수행 [1]
            update_account_alias(user_id)
        elif sub_choice == '3':
            # 요구사항 5번에 따라 계좌 삭제 기능 수행 [1]
            delete_my_account(user_id)
        elif sub_choice == '4':
            break
        else:
            print("[오류] 다시 선택해 주세요.")

#내 계좌 등록
def register_account(user_id):
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

                 # 2. 은행 선택 (요구사항 3번에 따라 지정된 은행만 가능) [1]
                print("제공 은행: 1.하나은행, 2.우리은행, 3.국민은행, 4.신한은행, 5.기업은행")
                bank_id = input("은행 번호를 선택하세요: ")
                
                # 3. 계좌번호 및 별칭 입력
                # (이전 대화에서 구현한 랜덤 계좌번호 생성 함수를 사용할 수도 있습니다)
                acc_num = input("등록할 계좌번호를 입력하세요: ")
                alias = input("계좌 별칭을 입력하세요 (선택사항): ")

                # 4. 잔액 랜덤 생성 (10,000원 ~ 100,000,000원)
                # 요구사항 12번(1,000원 이상)을 자동으로 만족함 [1]
                initial_balance = random.randint(10000, 100000000)
                print(f"\n[시스템] 초기 잔액은 {initial_balance:,d}원으로 감지 되었습니다.\n\t잔액이 맞지 않다면 관리자에게 문의 바랍니다.")

                # 5. ACCOUNTS 테이블에 데이터 삽입 [1]
                sql_account = """
                INSERT INTO ACCOUNTS (ACCOUNT_NUM, BANK_ID, USER_ID, BALANCE, ALIAS)
                VALUES (:1, :2, :3, :4, :5)
                """
                cursor.execute(sql_account, (acc_num, bank_id, user_id, initial_balance, alias))

                # 6. 최초 입금 내역을 TRANSACTIONS 테이블에 기록
                sql_trans = """
                INSERT INTO TRANSACTIONS (TRANS_ID, TO_ACCOUNT, AMOUNT, TRANS_TYPE)
                VALUES (SEQ_TRANS_ID.NEXTVAL, :1, :2, '입금(개설)')
                """
                cursor.execute(sql_trans, (acc_num, initial_balance))

                # 7. 트랜잭션 확정
                connection.commit()
                print(f"\n[성공] '{acc_num}' 계좌가 등록되었으며, 잔액은 {initial_balance:,d}원 입니다.")
    except Exception as e:
        print(f"[오류] 등록 실패: {e}")

#내 계좌 수정
def update_account_alias(user_id):
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

                # 2. 내 계좌 목록 조회 (은행명, 계좌번호, 현재 별칭 포함) [1]
                sql_list = """
                SELECT A.ACCOUNT_NUM, B.BANK_NAME, A.ALIAS
                FROM ACCOUNTS A
                JOIN BANKS B ON A.BANK_ID = B.BANK_ID
                WHERE A.USER_ID = :1
                """
                cursor.execute(sql_list, [user_id])
                my_accounts = cursor.fetchall()

                # 3. 계좌 존재 여부 확인 [1]
                if not my_accounts:
                    print("\n[알림] 수정할 계좌가 없습니다. 먼저 계좌를 등록해 주세요.")
                    return

                # 4. 계좌 목록 출력 및 선택
                print("\n--- [별칭을 수정할 계좌를 선택하세요] ---")
                for i, acc in enumerate(my_accounts, 1):
                    # acc[0]: 계좌번호, acc[1]: 은행명, acc[2]: 현재 별칭
                    current_alias = f" (현재 별칭: {acc[2]})" if acc[2] else " (별칭 없음)"
                    print(f"{i}. {acc[0]} | {acc[1]}{current_alias}")
                
                try:
                    choice = int(input("\n수정할 계좌 번호 선택: ")) - 1
                    if not (0 <= choice < len(my_accounts)):
                        print("[오류] 잘못된 번호입니다.")
                        return
                except ValueError:
                    print("[오류] 숫자만 입력 가능합니다.")
                    return

                selected_acc_num = my_accounts[choice][0]
                old_alias = my_accounts[choice][2]

                # 5. 새로운 별칭 입력 및 검증 [1]
                new_alias = input("새로운 별칭을 입력하세요: ")

                # 요구사항 4번: 같은 별칭으로는 수정 불가 [1]
                if new_alias == old_alias:
                    print(f"\n[오류] 현재 별칭('{old_alias}')과 동일한 별칭으로 수정할 수 없습니다.")
                    return

                # 6. DB 업데이트 수행
                sql_update = "UPDATE ACCOUNTS SET ALIAS = :1 WHERE ACCOUNT_NUM = :2 AND USER_ID = :3"
                cursor.execute(sql_update, [new_alias, selected_acc_num, user_id])
                
                # 7. 트랜잭션 확정
                connection.commit()
                print(f"\n[성공] '{selected_acc_num}' 계좌의 별칭이 '{new_alias}'(으)로 변경되었습니다.")
    except Exception as e:
        print(f"[오류] 수정 실패: ({new_alias}) 별칭을 쓰는 계좌가 이미 있습니다.")

# 내 계좌 삭제
def delete_my_account(user_id):
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

                # 2. 내 계좌 목록 조회 (요구사항 2번: 은행명, 계좌번호, 잔액, 별칭 포함)
                sql_list = """
                SELECT A.ACCOUNT_NUM, B.BANK_NAME, A.BALANCE, A.ALIAS
                FROM ACCOUNTS A
                JOIN BANKS B ON A.BANK_ID = B.BANK_ID
                WHERE A.USER_ID = :1
                """
                cursor.execute(sql_list, [user_id])
                my_accounts = cursor.fetchall()

                # 3. 계좌 존재 여부 확인
                if not my_accounts:
                    print("\n[알림] 삭제할 계좌가 없습니다.")
                    return

                # 4. 계좌 목록 출력 및 삭제할 계좌 선택
                print("\n--- [삭제할 내 계좌를 선택하세요] ---")
                for i, acc in enumerate(my_accounts, 1):
                    # acc[0]:계좌번호, acc[1]:은행명, acc[2]:잔액, acc[3]:별칭
                    alias_display = f"({acc[3]})" if acc[3] else ""
                    print(f"{i}. {acc[0]} | {acc[1]} | 잔액: {acc[2]:,d}원 {alias_display}")
                
                try:
                    choice = int(input("\n삭제할 계좌 번호 선택 (취소는 0): "))
                    if choice == 0:
                        print("[알림] 삭제를 취소합니다.")
                        return
                    if not (1 <= choice <= len(my_accounts)):
                        print("[오류] 잘못된 번호입니다.")
                        return
                except ValueError:
                    print("[오류] 숫자만 입력 가능합니다.")
                    return

                selected_acc_num = my_accounts[choice-1][0]

                # 5. 최종 삭제 확인
                confirm = input(f"정말로 '{selected_acc_num}' 계좌를 삭제하시겠습니까? 관련 거래 내역도 모두 삭제됩니다. (y/n): ")
                if confirm.lower() != 'y':
                    print("[알림] 삭제 작업이 취소되었습니다.")
                    return

                # 6. 데이터 삭제 수행 (외래 키 제약 조건 고려)
                # 먼저 해당 계좌와 관련된 거래 내역(TRANSACTIONS) 삭제
                sql_del_trans = "DELETE FROM TRANSACTIONS WHERE TO_ACCOUNT = :1"
                cursor.execute(sql_del_trans, [selected_acc_num])
                
                # 실제 계좌(ACCOUNTS) 삭제
                sql_del_acc = "DELETE FROM ACCOUNTS WHERE ACCOUNT_NUM = :1 AND USER_ID = :2"
                cursor.execute(sql_del_acc, [selected_acc_num, user_id])

                # 7. 트랜잭션 확정 (요구사항 13번 원칙 적용)
                connection.commit()
                print(f"\n[성공] '{selected_acc_num}' 계좌와 관련된 모든 정보가 삭제되었습니다.")

    except Exception as e:
        if connection: connection.rollback() # [2]
        print(f"[오류] 삭제 실패: {e}")