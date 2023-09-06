from nnfw_api_pybind import *

def main():

    session = nnfwSession()

    state = session.create()

    if state != NNFW_STATUS.NNFW_STATUS_NO_ERROR:
        print('nnfw_create_session error', state)
        return

    # nnpackage 로딩
    state = session.load_model_from_file("inception_v3")

    if state != NNFW_STATUS.NNFW_STATUS_NO_ERROR:
        print('nnfw_load_model_from_file error', state)
        return

    # CONV_2D는 acl_neon 백엔드를 사용하고, 그 외에는 acl_cl 백엔드를 사용합니다.
    # 기본 백엔드는 acl_cl입니다.
    state = session.set_op_backend("CONV_2D", "cpu")

    if state != NNFW_STATUS.NNFW_STATUS_NO_ERROR:
        print('nnfw_set_op_backend error')
        return

    # 모델 컴파일
    state = session.prepare()
    if state != NNFW_STATUS.NNFW_STATUS_NO_ERROR:
        print('nnfw_prepare error')
        return

    # 입력 데이터 준비. 여기서는 더미 입력 배열을 할당합니다.
    state = session.input_tensorinfo(0)  # 첫 번째 입력의 정보 가져오기
    if state != NNFW_STATUS.NNFW_STATUS_NO_ERROR:
        print('nnfw_input_tensorinfo error')
        return
    
    state = session.set_input(0)
    if state != NNFW_STATUS.NNFW_STATUS_NO_ERROR:
        print('nnfw_set_input error')
        return

    # 출력 데이터 준비
    state = session.output_tensorinfo(0)  # 첫 번째 출력의 정보 가져오기
    if state != NNFW_STATUS.NNFW_STATUS_NO_ERROR:
        print('nnfw_output_tensorinfo error')
        return
    
    state = session.set_output(0)
    if state != NNFW_STATUS.NNFW_STATUS_NO_ERROR:
        print('nnfw_set_output error')
        return
    
    # 추론 실행
    state = session.run()
    if state != NNFW_STATUS.NNFW_STATUS_NO_ERROR:
        print('nnfw_run error')
        return

    # TODO: 출력 값을 원하는 방식으로 출력하거나 비교합니다.
    state = session.close()

    if state != NNFW_STATUS.NNFW_STATUS_NO_ERROR:
        print('nnfw_close_session error')
        return
    else:
        print("nnpackage가 성공적으로 실행되었습니다.")

if __name__ == "__main__":
    main()
