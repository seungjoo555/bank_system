from bankSystemRegister import register_user
from bankLogin import login_user
from bankCreateAccount import create_account
from bankSearchAccount import view_accounts
from bankMyMenu import manage_my_accounts
from bankDeposit import deposit_money
from bankWithdraw import withdraw_money
from bankTransfer import transfer,transfer_db
from bankViewHistory import view_all_history
import bankAdmin as ad

def main():

    while True:
        # 시작 -> 메인 메뉴 [1]
        print("\n" + "="*20)
        print("  메인 메뉴")
        print("="*20)
        print("1. 회원가입")
        print("2. 로그인")
        print("3. 종료")
        print("="*20)
        
        choice = input("원하는 메뉴 번호를 입력하세요: ")

        if choice == '1':
            # 이전 대화에서 구현한 register_user() 함수를 호출할 수 있습니다.
            print("\n[안내] 회원가입 화면으로 이동합니다.")
            register_user() 
            continue
        elif choice == '2':
            # 로그인 성공 시 '은행 메뉴'로 진입하는 로직 [1]
            print("\n[안내] 로그인을 진행합니다.")
            is_logged_in = login_user() # (로그인 성공 가정)
            if is_logged_in[0] and is_logged_in [3] == 'ADMIN':
                admin_menu()
            elif is_logged_in[0]:
                bank_menu(*is_logged_in)
        elif choice == '3':
            print("\n[안내] 프로그램을 종료합니다. 이용해 주셔서 감사합니다.")
            break
        else:
            print("\n[오류] 잘못된 입력입니다. 1~3번 사이의 번호를 입력해 주세요.")

def bank_menu(*user_info):
    while True:
        # 로그인 성공 후 -> 은행 메뉴 [1]
        print("\n" + "="*20)
        print("  은행 메뉴")
        print("="*20)
        print("1. 내 계좌 생성")
        print("2. 내 계좌 조회")
        print("3. 내 계좌 관리")  # 요구사항 5번 반영
        print("4. 입금")
        print("5. 출금")
        print("6. 계좌이체")
        print("7. 다른 데이터베이스 계좌이체")
        print("8. 거래내역 조회")
        print("9. 로그아웃")
        print("="*20)

        choice = input("원하는 업무 번호를 입력하세요: ")

        if choice == '1':
            create_account(user_info[1])
        elif choice == '2':
            view_accounts(user_info[1])
        elif choice == '3':
            # 내 계좌 관리 서브 메뉴 호출
            manage_my_accounts(user_info[1])
        elif choice == '4':
            deposit_money(user_info[1])
        elif choice == '5':
            withdraw_money(user_info[1])
        elif choice == '6':
            transfer(user_info[1])
        elif choice == '7':
            transfer_db(user_info[1])
        elif choice == '8':
            view_all_history(user_info[1])
        elif choice == '9':
            print("\n[안내] 로그아웃 되었습니다.")
            break
        else:
            print("\n[오류] 잘못된 입력입니다.")

def admin_menu():
    while True:
        #관리자 계정으로 로그인 했을때의 메뉴
        print("\n" + "="*20)
        print("  관리자 메뉴")
        print("="*20)
        print("1. 사용자 정보 조회")
        print("2. 사용자 정보 수정")
        print("3. 사용자 정보 삭제")
        print("4. 로그아웃")
        print("="*20)

        admin_choice = input("원하는 업무 번호를 입력하세요: ")

        if admin_choice == '1':
            ad.admin_view_users()
        elif admin_choice == '2':
            ad.admin_update_user()
        elif admin_choice == '3':
            ad.admin_delete_user()
        elif admin_choice == '4':
            print("\n[안내] 로그아웃 되었습니다. 메인 메뉴로 돌아갑니다.")
            break
        else:
            print("\n[오류] 잘못된 입력입니다. 1~4번 사이의 번호를 입력해 주세요.")

if __name__ == "__main__":
    main()