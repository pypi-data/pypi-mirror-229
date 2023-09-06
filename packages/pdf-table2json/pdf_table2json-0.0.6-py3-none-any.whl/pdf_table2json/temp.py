import os
import shutil
import cv2
import numpy as np
import json
import argparse

import fitz  # PyMuPDF # text extractor
import util  # package # utf-8


# 워터마크를 제거
def f_remove_watermark(image, target_color):
    # 제거할 워터마크 색상과 유사한 픽셀 찾기
    diff = np.abs(image - target_color)
    mask = np.all(diff <= 20, axis=-1)
    # 제거할 픽셀을 백색으로 채우기
    image[mask] = [255, 255, 255]

    return image


# 보더라인 추가 (특정 색, 최소 가로 값 기준)
def f_add_border_lines(image):
    # 특정 색상 추출 (#E6E6E6)
    lower_color = np.array([230, 230, 230])  # BGR 형식으로 변환
    upper_color = np.array([230, 230, 230])  # BGR 형식으로 변환
    mask = cv2.inRange(image, lower_color, upper_color)

    # 추출된 색상의 외곽선 찾기
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 외곽선 주위에 border 그리기
    border_thickness = 2
    border_color = (0, 0, 0)  # 검정

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if w >= 1000:  # 특정 가로 길이 이상일 때 (테이블 인식 기준과 동일하게)
            cv2.rectangle(image, (x, y), (x + w, y + h), border_color, border_thickness)

    return image


# 행 구분해서 값 리스트로 저장
def f_process_list(input_list):
    result_list = []
    current_group = []
    prev_length = None

    for item in input_list:
        current_length = len(item)

        if prev_length is None:
            prev_length = current_length
            current_group = [item]
        elif prev_length == current_length:
            current_group.append(item)
        else:
            result_list.append(current_group)
            current_group = [item]
            prev_length = current_length

    if current_group:
        result_list.append(current_group)


    return result_list


# PDF 페이지 이미지로 변환 함수
def f_convert_pdf_to_images(pdf_path, output_dir):
    pdf_document = fitz.open(pdf_path)

    os.makedirs(output_dir, exist_ok=True)
    print(output_dir)

    image_paths = []  # 생성된 이미지 파일 경로를 저장할 리스트

    for page_number in range(pdf_document.page_count):
        page = pdf_document[page_number]
        pixmap = page.get_pixmap(matrix=fitz.Matrix(300 / 72, 300 / 72))  # DPI 설정

        image_path = os.path.join(output_dir, f"page_{page_number + 1}.png")
        pixmap.save(image_path, "png")
        image_paths.append(image_path)

        print(f"Page {page_number + 1} converted to image: {image_path}")

    # pdf_document.close()
    return image_paths, pdf_document, page_number  # 생성된 이미지 파일 경로들을 반환

# 경로 처리
def path_parse(input_pdf_path):
    dir_path, name_extension = os.path.split(input_pdf_path)
    name, _ = os.path.splitext(name_extension)

    # dir_path : 경로
    # name_extension : 등기부등본.pdf
    # name : 등기부등본
    # print(dir_path)
    # print(name_extension)
    # print(name)

    return dir_path, name_extension, name

# input_pdf_path : 경로/이름.확장자
# output_path : 경로
# processed_img_out : 처리 이미지 저장
# json_file_out : JSON 파일 저장
def main(input_pdf_path, output_path=None, json_file_out=None, processed_img_out=None):

    if output_path is None:
        # output_path가 제공되지 않은 경우, input_path와 동일한 경로를 사용
        output_path = input_pdf_path

    dir_path, name_extension, name = path_parse(input_pdf_path)
    dir_path_out, _, _ = path_parse(output_path)
    
    # PDF 파일 경로 설정
    pdf_path = input_pdf_path # pdf 경로
    pdf_name = name_extension
    output_dir = dir_path_out + "/" + name + "/"  # 원본 이미지, JSON 저장할 디렉토리

    # 처리한 이미지를 저장할 디렉토리 설정
    if processed_img_out:
        line_image_dir =  output_dir + "/processed_images/"
        os.makedirs(line_image_dir, exist_ok=True)
    
    # 이미지 변환 실행
    image_paths, pdf_document, page_number = f_convert_pdf_to_images(pdf_path, output_dir)

    # JSON 데이터 누적
    accumulated_json_data = []

    # 페이지 순환
    for page_number, image_path in enumerate(image_paths, start=0):

        # 이미지 로드
        image = util.utf_imread(image_path)
        
        # 이미지 크기 (행과 열의 픽셀 수)
        image_height, image_width, _ = image.shape

        # 이미지 전처리
        #precessed_image = f_image_preocessing(image)

        # 보더라인 추가 (특정 색, 최소 가로 값 기준)
        added_border_image = f_add_border_lines(image)

        # 워터마크 색상 (특정 색 지정)
        watermark_color_1 = (213, 213, 213)  # D5D5D5
        watermark_color_2 = (224, 224, 224)  # E0E0E0

        # 워터마크 제거
        removed_watermark_image = f_remove_watermark(added_border_image, watermark_color_1)
        removed_watermark_image = f_remove_watermark(removed_watermark_image, watermark_color_2)

        # 그레이스케일로 변환
        gray_image = cv2.cvtColor(removed_watermark_image, cv2.COLOR_BGR2GRAY)

        # 가우시안 블러 적용
        blurred_image = cv2.GaussianBlur(gray_image, (5, 5), 0)

        # 이미지 이진화
        _, thresholded_image = cv2.threshold(blurred_image, 200, 255, cv2.THRESH_BINARY)

        # 이미지 Canny 에지 검출
        edges = cv2.Canny(thresholded_image, threshold1=50, threshold2=150)

        # 윤곽선 찾기
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # 모든 테이블의 좌표와 크기를 저장할 리스트
        tables = []

        line_image = image.copy()

        # 모든 테이블의 윤곽선 찾기
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if w > 1000 and h > 100:  # 테이블 크기 조건을 설정하여 임계값 이상 크기의 테이블만 선택
                tables.append((x, y, w, h))

        # 테이블 리스트를 좌측 상단부터 시작하도록 정렬
        tables.reverse()

        # PDF 페이지 로드
        pdf_page = pdf_document[page_number]  # PDF 페이지 번호

        # PDF 페이지의 크기 가져오기 (포인트 단위)
        pdf_page_width = pdf_page.rect.width
        pdf_page_height = pdf_page.rect.height

        # 이전 행의 칼럼 개수와 행 정보를 저장할 리스트
        prev_column_count = None
        row_list = []

        # 테이블 순환
        for table_number, (x, y, w, h) in enumerate(tables, start=1):

            if table_number == 1:  # 첫 번째 테이블일 때 new_list 초기화 (테이블 변경 시 list 초기화)
                new_list = []

            # 테이블 내부에서만 셀을 찾아서 화면에 순번 출력 및 정보 출력
            roi = thresholded_image[y:y + h, x:x + w]
            cell_contours, _ = cv2.findContours(roi, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # 셀 순번 초기화
            cell_number = 1

            # 로우별 셀 그룹을 관리하는 딕셔너리 초기화
            cell_rows = {}

            # 셀 오름차순 정렬
            cell_contours = sorted(cell_contours, key=lambda c: cv2.boundingRect(c)[1])

            for idx, contour in enumerate(cell_contours):
                x_cell, y_cell, w_cell, h_cell = cv2.boundingRect(contour)
                x_global, y_global = x + x_cell, y + y_cell

                # 넘어갈 값, 너무 작거나, 테이블의 가로 또는 세로의 크기와 같거나 (1행1열의 셀 하나를 표라고 볼 수 없게 됨 - 이후에 테이블로 보는데, 0행 0열)
                if w == w_cell or h == h_cell or w_cell <= 10 or h_cell <= 10:
                    continue

                # 이미지에 사각형 그리기, 텍스트 작성
                cv2.rectangle(line_image, (x_global, y_global), (x_global + w_cell, y_global + h_cell), (0, 255, 0), 2)
                cv2.putText(line_image, f"[T_{table_number} C_{cell_number}]", (x_global + w_cell // 2, y_global + h_cell // 2), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 0, 0), 2)

                # 이미지 좌표를 PDF 좌표로 변환
                pdf_x1 = x_global * (pdf_page_width / image_width)
                pdf_y1 = y_global * (pdf_page_height / image_height)
                pdf_x2 = (x_global + w_cell) * (pdf_page_width / image_width)
                pdf_y2 = (y_global + h_cell) * (pdf_page_height / image_height)

                # PDF 텍스트 추출
                text = pdf_page.get_text("text", clip=(pdf_x1, pdf_y1, pdf_x2, pdf_y2))

                # 셀 그룹화
                if y_global not in cell_rows:
                    cell_rows[y_global] = []
                cell_rows[y_global].append({
                    "x": x_global,
                    "y": y_global,
                    "width": w_cell,
                    "height": h_cell,
                    "text": text.strip()
                })

                # 셀 순번 증가
                cell_number += 1

                # 새로운 테이블을 처리하기 전에 new_list 초기화
                if idx == 0:
                    new_list = []

                # 로우별 셀 그룹을 row_list에 추가
                new_list = f_process_list(list(cell_rows.values()))


            # 데이터를 JSON 형식으로 정리
            data_list = []
            for idx, group in enumerate(new_list):
                text_values = [item["text"] for row in group for item in row]
                row_length = len(group[0])  # 로우의 길이
                grouped_text_values = [list(reversed(text_values[i:i + row_length])) for i in range(0, len(text_values), row_length)]
                data_list.append({"row": idx, "columns": grouped_text_values})
            # JSON 형식으로 출력 (UTF-8 인코딩)
            json_data = json.dumps(data_list, indent=4, ensure_ascii=False)

            #print(">>>>>>>>>>>>>>>>>>>>>>>>>>")
            #print(json_data)

            # JSON 데이터 누적
            accumulated_json_data.append(json_data)

            # 새로운 테이블을 처리하기 전에 데이터 초기화
            prev_column_count = None
            row_list = []

        # 이미지 초기화
        image = None

        # processed_image 저장
        if processed_img_out:
            f_make_processed_img(line_image_dir, page_number, line_image)

    # 데이터를 JSON 형식으로 출력
    json_data_combined = json.dumps(accumulated_json_data, indent=4, ensure_ascii=False)
    
    # JSON 데이터를 파일로 저장
    if json_file_out:
        f_make_json_file(json_data_combined, output_dir, pdf_name)

    # PDF 문서 닫기
    pdf_document.close()

    # 원본 이미지 디렉터리 삭제
    # f_delete_directory(output_dir)

    return json_data_combined

def f_make_processed_img(output_dir, page_number, processed_image):
    line_image_path = os.path.join(output_dir, f"processed_image_{page_number + 1}.png")
    util.utf_imwrite(line_image_path, processed_image)
    print(f"Line image for page {page_number + 1} saved to {line_image_path}")

def f_make_json_file(data, output_dir, pdf_name):
    # JSON 데이터를 파일로 저장
    combined_output_path = output_dir + pdf_name + ".json"
    with open(combined_output_path, "w", encoding="utf-8") as combined_output_file:
        combined_output_file.write(data)
    print("JSON data saved to", combined_output_path)

# PDF to Image 디렉터리 삭제
def f_delete_directory(path):
    try:
        # 지정된 경로의 디렉터리와 하위 파일 및 디렉터리를 모두 삭제
        shutil.rmtree(path)
        print(f"Removed directory : {path} ")
    except Exception as e:
        print(f"Error removing directory: {str(e)}")

'''
"C:/Users/aria1/OneDrive/바탕 화면/프로젝트/pdf처리/자료/등기부등본모음/"

python a.py -i "C:/Users/aria1/OneDrive/바탕 화면/프로젝트/pdf처리/자료/등기부등본모음/아파트등기2_용산구.pdf" -o "C:/Users/aria1/OneDrive/바탕 화면/프로젝트/"
'''
        
def is_valid_pdf(file_path):
    # 파일 경로로부터 확장자 추출
    file_extension = os.path.splitext(file_path)[-1].lower()
    # 확장자가 .pdf 인지 확인
    return file_extension == '.pdf'

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract tables from PDF files To JSON data")
    parser.add_argument("-i", "--input", required=True, help="Input PDF file path")
    parser.add_argument("-o", "--output", default=None, help="[Optional] Output directory to save the extracted datas")
    parser.add_argument("-j", "--json_file", default=None, help="[Optional] JSON Data file out")
    parser.add_argument("-p", "--image", default=None, help="[Optional] Processed Image file out")
    args = parser.parse_args()

    input_path = args.input
    output_dir = args.output
    json_file_out = args.json_file
    processed_img_out = args.image

    if not is_valid_pdf(input_path):
        print("Input file is not a valid PDF file.")
    elif not (output_dir or json_file_out or processed_img_out):
        main(input_path, output_dir, None, None)
        print("No output path specified. PDF will not be saved.")
    else:
        main(input_path, output_dir, json_file_out, processed_img_out)
