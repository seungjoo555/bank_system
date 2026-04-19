import oracledb
import random

#관리자 - 사용자 정보 조회
def admin_view_users():
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

                # 사용자 아이디, 계좌주명, 권한을 조회
                sql = "SELECT USER_ID, USER_NAME, ROLE FROM USERS ORDER BY USER_ID"
                cursor.execute(sql)
                users = cursor.fetchall()

                print("\n" + "="*40)
                print(f"{'사용자 ID':<15} | {'계좌주명':<10} | {'권한':<10}")
                print("-" * 40)

                if not users:
                    print("등록된 사용자가 없습니다.")
                else:
                    for uid, uname, role in users:
                        print(f"{uid:<15} | {uname:<10} | {role:<10}")
                print("="*40)

    except Exception as e:
        print(f"\n[시스템 에러] 사용자 조회 중 오류 발생: {e}")

#관리자 - 사용자 정보 수정
def admin_update_user():
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

                print("\n--- [사용자 정보 수정] ---")
                user_id = input("수정할 사용자의 ID를 입력하세요: ")

                # 1. 사용자 존재 여부 확인
                cursor.execute("SELECT USER_NAME FROM USERS WHERE USER_ID = :1", [user_id])
                user_data = cursor.fetchone()

                if not user_data:
                    print(f"[알림] ID '{user_id}'에 해당하는 사용자가 존재하지 않습니다.")
                    return

                print(f"현재 선택된 사용자: {user_data}({user_id})")
                print("1. 비밀번호 수정")
                print("2. 계좌주명 수정")
                print("3. 취소")
                
                choice = input("수정할 항목을 선택하세요: ")

                if choice == '1':
                    new_password = input("새로운 비밀번호를 입력하세요: ")
                    sql = "UPDATE USERS SET PASSWORD = :1 WHERE USER_ID = :2"
                    cursor.execute(sql, [new_password, user_id])
                    print(f"\n[성공] '{user_id}' 사용자의 비밀번호가 변경되었습니다.")

                elif choice == '2':
                    new_name = input("새로운 계좌주명을 입력하세요: ")
                    sql = "UPDATE USERS SET USER_NAME = :1 WHERE USER_ID = :2"
                    cursor.execute(sql, [new_name, user_id])
                    print(f"\n[성공] '{user_id}' 사용자의 계좌주명이 '{new_name}'(으)로 변경되었습니다.")
                
                elif choice == '3':
                    print("[알림] 수정을 취소합니다.")
                    return
                else:
                    print("[오류] 잘못된 선택입니다.")
                    return

                # 2. 트랜잭션 확정
                connection.commit()

    except Exception as e:
        if connection:
            connection.rollback()
        print(f"\n[시스템 에러] 정보 수정 중 오류 발생: {e}")

#관리자 - 사용자 정보 삭제
def admin_delete_user():
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

                print("\n--- [사용자 정보 전체 삭제] ---")
                user_id = input("삭제할 사용자의 ID를 입력하세요: ")

                # 1. 사용자 존재 확인
                cursor.execute("SELECT USER_NAME FROM USERS WHERE USER_ID = :1", [user_id])
                user_data = cursor.fetchone()

                if not user_data:
                    print(f"[알림] ID '{user_id}'에 해당하는 사용자가 존재하지 않습니다.")
                    return

                # 2. 삭제 확인 절차 (중요 데이터 삭제이므로 확인 필수)
                confirm = input(f"정말로 '{user_data}({user_id})' 사용자의 모든 데이터를 삭제하시겠습니까? (y/n): ")
                if confirm.lower() != 'y':
                    print("[알림] 삭제 작업이 취소되었습니다.")
                    return

                # 3. 데이터 삭제 수행 (외래 키 제약 조건을 고려한 순서)
                
                # A. TRANSACTIONS 삭제: 해당 사용자의 계좌가 연루된 모든 거래 내역 삭제
                sql_del_trans = """
                DELETE FROM TRANSACTIONS 
                WHERE TO_ACCOUNT IN (SELECT ACCOUNT_NUM FROM ACCOUNTS WHERE USER_ID = :user_id)
                OR FROM_ACCOUNT IN (SELECT ACCOUNT_NUM FROM ACCOUNTS WHERE USER_ID = :user_id)
                """
                cursor.execute(sql_del_trans, {'user_id':user_id})
                
                # B. ACCOUNTS 삭제: 해당 사용자가 소유한 모든 계좌 삭제 [2]
                sql_del_accs = "DELETE FROM ACCOUNTS WHERE USER_ID = :1"
                cursor.execute(sql_del_accs, [user_id])
                
                # C. USERS 삭제: 회원 정보 삭제 [1]
                sql_del_user = "DELETE FROM USERS WHERE USER_ID = :1"
                cursor.execute(sql_del_user, [user_id])

                # 4. 트랜잭션 확정 (요구사항 13번: 모든 과정이 성공했을 때만 반영) [1]
                connection.commit()
                print(f"\n[성공] '{user_id}' 사용자와 관련된 모든 정보가 안전하게 삭제되었습니다.")

    except Exception as e:
        print(e)
        # 요구사항 13번 반영: 문제 발생 시 모든 작업 취소 [1]
        if connection:
            connection.rollback()
        print(f"\n[시스템 에러] 삭제 처리 중 오류 발생으로 모든 작업이 취소되었습니다: {e}")